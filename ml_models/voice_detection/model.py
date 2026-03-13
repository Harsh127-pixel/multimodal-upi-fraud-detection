import torch
import torch.nn as nn
import torch.nn.functional as F

class VoiceCNN(nn.Module):
    """
    CNN architecture for Voice Deepfake Detection.
    Inputs: Mel Spectrogram tensors (Batch, 1, Mel_Bands, Time)
    """
    def __init__(self):
        super(VoiceCNN, self).__init__()
        
        # Layer 1: Conv2D (32 filters) + ReLU + MaxPool
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Layer 2: Conv2D (64 filters) + ReLU
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        
        # Layer 3: Global Average Pooling
        # Reduces spatial dimensions (H, W) to (1, 1) regardless of input size
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # Layer 4: Fully Connected
        self.fc = nn.Linear(64, 1)
        
        # Layer 5: Sigmoid Output
        # 0.0 to 1.0 (Probability of being 'Fake')
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # Input x: (Batch, 1, 128, Time)
        
        # Block 1
        x = self.pool(F.relu(self.conv1(x)))
        
        # Block 2
        x = F.relu(self.conv2(x))
        
        # Global Avg Pool
        x = self.global_pool(x)
        
        # Flatten for FC layer
        x = torch.flatten(x, 1)
        
        # FC + Sigmoid
        x = self.fc(x)
        x = self.sigmoid(x)
        
        return x

if __name__ == "__main__":
    # Quick architecture check
    model = VoiceCNN()
    test_input = torch.randn(1, 1, 128, 500) # (Batch, Channel, Mels, Time)
    output = model(test_input)
    print(f"Model Summary:\n{model}")
    print(f"\nTest Output Shape: {output.shape} (Probability of Fake)")
