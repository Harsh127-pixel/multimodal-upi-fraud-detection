import librosa
import numpy as np
import torch

class VoiceFeatureExtractor:
    def __init__(self, sr=16000, n_mels=128, n_fft=2048, hop_length=512):
        """
        Initializes the feature extractor.
        
        Args:
            sr (int): Sampling rate for audio.
            n_mels (int): Number of Mel bands to generate.
            n_fft (int): Length of the FFT window.
            hop_length (int): Number of samples between successive frames.
        """
        self.sr = sr
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length

    def load_audio(self, file_path):
        """Loads an audio file and resamples it to the target sampling rate."""
        y, _ = librosa.load(file_path, sr=self.sr)
        return y

    def compute_mel_spectrogram(self, y):
        """Computes a log-mel spectrogram from an audio signal."""
        # Generate Mel Spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=y, 
            sr=self.sr, 
            n_fft=self.n_fft, 
            hop_length=self.hop_length, 
            n_mels=self.n_mels
        )
        # Convert to decibel (log) scale
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        return mel_spec_db

    def to_tensor(self, mel_spec_db):
        """
        Converts the mel spectrogram to a PyTorch tensor formatted for CNN input.
        Shape: (1, n_mels, time_steps) -> (Channel, Frequency, Time)
        """
        # Add channel dimension
        tensor_input = torch.tensor(mel_spec_db).unsqueeze(0)
        return tensor_input

    def extract(self, file_path):
        """Pipeline to convert an audio file path directly to a CNN-ready tensor."""
        y = self.load_audio(file_path)
        mel_spec = self.compute_mel_spectrogram(y)
        return self.to_tensor(mel_spec)

if __name__ == "__main__":
    # Quick test if run as script
    extractor = VoiceFeatureExtractor()
    print("Feature Extractor ready for processing.")
