import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm

from .model import VoiceCNN
from .dataset_loader import ASVspoofDataset

def train():
    # 1. Configuration & Paths
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    # Update these paths relative to your local setup
    PROTOCOL_FILE = r"e:\Software\multimodal-upi-fraud-detection\dataset\voice_deepfake\LA\ASVspoof2019_LA_cm_protocols\ASVspoof2019.LA.cm.train.trn.txt"
    DATA_DIR = r"e:\Software\multimodal-upi-fraud-detection\dataset\voice_deepfake\LA\ASVspoof2019_LA_train\flac"
    SAVE_PATH = "voice_detection_model.pth"

    epochs = 5
    batch_size = 32
    learning_rate = 0.001

    # 2. Dataset & Loader
    print("Loading dataset...")
    # Using a subset (max_samples) if you want to test quickly; remove for full training
    train_dataset = ASVspoofDataset(PROTOCOL_FILE, DATA_DIR, max_samples=None) 
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    # 3. Model, Loss, Optimizer
    model = VoiceCNN().to(device)
    criterion = nn.BCELoss() # Binary Cross Entropy for single-probability output
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # 4. Training Loop
    print("Starting training...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        # Use tqdm for a nice progress bar
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        
        for inputs, labels in progress_bar:
            inputs = inputs.to(device)
            # Reshape labels to (Batch, 1) to match sigmoid output shape
            labels = labels.float().unsqueeze(1).to(device)
            
            # Forward pass
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            # Backward pass & Optimizer step
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Update metrics
            running_loss += loss.item()
            progress_bar.set_postfix(loss=f"{loss.item():.4f}")
            
        avg_loss = running_loss / len(train_loader)
        print(f"Epoch {epoch+1} Complete. Average Loss: {avg_loss:.4f}")

    # 5. Save the model
    torch.save(model.state_dict(), SAVE_PATH)
    print(f"Model saved to {SAVE_PATH}")

if __name__ == "__main__":
    train()
