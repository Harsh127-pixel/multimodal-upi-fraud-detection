import torch
import torch.nn as nn

class VoiceDeepfakeModel(nn.Module):
    def __init__(self, input_size=1600):  # 40 n_mfcc * 40 max_pad_len = 1600
        super(VoiceDeepfakeModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1),
            nn.Sigmoid() # Outputs a probability between 0 and 1
        )

    def forward(self, x):
        return self.network(x)

def load_model(weights_path=None):
    """
    Loads the PyTorch Deepfake Detection Model.
    If weights_path is provided, loads the saved state dict.
    """
    model = VoiceDeepfakeModel()
    
    if weights_path:
        try:
            model.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
            print(f"Successfully loaded weights from {weights_path}")
        except Exception as e:
            print(f"Warning: Could not load weights: {e}. Using an untrained model.")
            
    # Set to evaluation mode for inference
    model.eval()
    return model

def predict_is_real(model, features):
    """
    Given the model and flattened MFCC features, returns the probability of the audio being a "real voice".
    1.0 -> Real
    0.0 -> Deepfake
    """
    # Convert numpy array to PyTorch tensor and add a batch dimension
    # Shape changes from (1600,) to (1, 1600)
    tensor_features = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
    
    with torch.no_grad():
        output = model(tensor_features)
        
    # Extract the scalar value from the output tensor
    probability = output.item()
    return probability
