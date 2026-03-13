import torch
import os
from .model import VoiceCNN
from .feature_extractor import VoiceFeatureExtractor

class VoicePredictor:
    """
    Predictor class to handle inference for voice deepfake detection.
    """
    def __init__(self, model_path="voice_detection_model.pth"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.extractor = VoiceFeatureExtractor()
        
        # Load Model
        self.model = VoiceCNN().to(self.device)
        if os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print(f"Model loaded from {model_path}")
        else:
            print(f"Warning: Model file {model_path} not found. Using uninitialized weights.")
        
        self.model.eval()

    def predict(self, audio_path):
        """
        Predicts if an audio file is real or fake.
        
        Returns:
            prob (float): Probability of being 'Fake' (0.0 to 1.0)
            label (str): Classification string
        """
        try:
            # 1. Feature Extraction
            # Result is a tensor of shape (1, n_mels, time)
            feature_tensor = self.extractor.extract(audio_path)
            
            # 2. Add batch dimension -> (1, 1, n_mels, time)
            feature_tensor = feature_tensor.unsqueeze(0).to(self.device)
            
            # 3. Model Inference
            with torch.no_grad():
                prob_tensor = self.model(feature_tensor)
                prob = prob_tensor.item() # Sigmoid output
            
            # 4. Label Assignment
            label = "Fake Voice" if prob >= 0.5 else "Real Voice"
            
            return prob, label

        except Exception as e:
            return None, f"Error: {str(e)}"

if __name__ == "__main__":
    # Test prediction
    # Replace with a path to an actual .flac or .wav file from your dataset
    TEST_AUDIO = r"e:\Software\multimodal-upi-fraud-detection\backend\dummy.wav" 
    
    predictor = VoicePredictor()
    
    if os.path.exists(TEST_AUDIO):
        probability, result = predictor.predict(TEST_AUDIO)
        if probability is not None:
            print(f"\nPrediction Results:")
            print(f"Probability: {probability:.4f}")
            print(f"Result: {result}")
        else:
            print(f"Prediction failed: {result}")
    else:
        print(f"Test file not found at {TEST_AUDIO}")
