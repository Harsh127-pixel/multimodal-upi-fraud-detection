import os
import torch
from torch.utils.data import Dataset, DataLoader
from .feature_extractor import VoiceFeatureExtractor

class ASVspoofDataset(Dataset):
    """
    Dataset class for ASVspoof2019 Logical Access (LA).
    Reads the protocol file and loads audio features.
    """
    def __init__(self, protocol_file, data_dir, feature_extractor=None, max_samples=None):
        """
        Args:
            protocol_file (str): Path to the ASVspoof protocol TXT file.
            data_dir (str): Path to the directory containing audio files (e.g., .../flac/).
            feature_extractor (VoiceFeatureExtractor): Extractor instance.
            max_samples (int, optional): Limit dataset size for quick testing.
        """
        self.data_dir = data_dir
        self.extractor = feature_extractor or VoiceFeatureExtractor()
        self.samples = []
        
        # Label mapping: bonafide -> 0, spoof -> 1
        self.label_map = {"bonafide": 0, "spoof": 1}

        # Parse protocol file
        if not os.path.exists(protocol_file):
            raise FileNotFoundError(f"Protocol file not found: {protocol_file}")

        with open(protocol_file, 'r') as f:
            lines = f.readlines()
            if max_samples:
                lines = lines[:max_samples]
                
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    speaker_id = parts[0]
                    file_id = parts[1]
                    # Skip parts[2], parts[3] (unused system info)
                    label_str = parts[4]
                    
                    file_path = os.path.join(self.data_dir, f"{file_id}.flac")
                    label = self.label_map.get(label_str, 1) # Default to spoof if unknown
                    
                    self.samples.append((file_path, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        file_path, label = self.samples[idx]
        
        try:
            # Extract features (mel spectrogram tensor)
            feature_tensor = self.extractor.extract(file_path)
            # Label as long tensor
            label_tensor = torch.tensor(label, dtype=torch.long)
            
            return feature_tensor, label_tensor
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            # Return zero tensor as fallback (or handle appropriately)
            dummy_feat = torch.zeros((1, 128, 500)) # Placeholder shape
            return dummy_feat, torch.tensor(label, dtype=torch.long)

def get_dataloader(protocol_file, data_dir, batch_size=32, shuffle=True, num_workers=0):
    """Factory function to create a DataLoader for the dataset."""
    dataset = ASVspoofDataset(protocol_file, data_dir)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers)

if __name__ == "__main__":
    # Test paths (update as needed for your local environment)
    PROTO = r"e:\Software\multimodal-upi-fraud-detection\dataset\voice_deepfake\LA\ASVspoof2019_LA_cm_protocols\ASVspoof2019.LA.cm.train.trn.txt"
    DATA = r"e:\Software\multimodal-upi-fraud-detection\dataset\voice_deepfake\LA\ASVspoof2019_LA_train\flac"
    
    if os.path.exists(PROTO):
        print("Testing Dataset Loader...")
        dataset = ASVspoofDataset(PROTO, DATA, max_samples=10)
        print(f"Successfully loaded {len(dataset)} samples.")
        feat, label = dataset[0]
        print(f"Feature shape: {feat.shape}, Label: {label}")
    else:
        print("Protocol file not found at test path.")
