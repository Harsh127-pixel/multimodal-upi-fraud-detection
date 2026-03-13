import torch
import os
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from tqdm import tqdm

from .model import VoiceCNN
from .dataset_loader import ASVspoofDataset

def evaluate(model_path="voice_detection_model.pth", max_samples=1000):
    """
    Evaluates the trained model on the development/evaluation dataset.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Evaluating on device: {device}")

    # Update paths for Dev/Eval set
    # Note: Using the Dev set protocol for evaluation by default
    PROTOCOL_FILE = r"e:\Software\multimodal-upi-fraud-detection\dataset\voice_deepfake\LA\ASVspoof2019_LA_cm_protocols\ASVspoof2019.LA.cm.dev.trl.txt"
    DATA_DIR = r"e:\Software\multimodal-upi-fraud-detection\dataset\voice_deepfake\LA\ASVspoof2019_LA_dev\flac"

    if not os.path.exists(model_path):
        print(f"Error: Model weights not found at {model_path}")
        return

    # 1. Load Model
    model = VoiceCNN().to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()

    # 2. Dataset & Loader
    print("Loading evaluation dataset...")
    dataset = ASVspoofDataset(PROTOCOL_FILE, DATA_DIR, max_samples=max_samples)
    loader = DataLoader(dataset, batch_size=32, shuffle=False)

    all_preds = []
    all_targets = []

    # 3. Inference Loop
    print("Running evaluation...")
    with torch.no_grad():
        for inputs, labels in tqdm(loader, desc="Testing"):
            inputs = inputs.to(device)
            
            # Forward pass
            outputs = model(inputs) # Sigmoid probabilities
            preds = (outputs >= 0.5).int().flatten().cpu().numpy()
            
            all_preds.extend(preds)
            all_targets.extend(labels.numpy())

    # 4. Metrics
    print("\n--- Evaluation Results ---")
    print(f"Accuracy: {accuracy_score(all_targets, all_preds):.4f}")
    print("\nClassification Report:")
    print(classification_report(all_targets, all_preds, target_names=["Real", "Fake"]))
    
    print("Confusion Matrix:")
    print(confusion_matrix(all_targets, all_preds))

if __name__ == "__main__":
    evaluate()
