import librosa
import numpy as np
import io
import soundfile as sf

def extract_mfcc(file_bytes, max_pad_len=40):
    """
    Extract MFCC features from an audio file buffer.
    
    Args:
        file_bytes (bytes): The raw audio bytes from the uploaded file.
        max_pad_len (int): The target length for padding/truncating the sequence.
        
    Returns:
        np.ndarray: MFCC features flattened as a NumPy array.
    """
    try:
        # Load audio from memory chunk using soundfile
        audio, sample_rate = sf.read(io.BytesIO(file_bytes))
        
        # If stereo, convert to mono by averaging the channels
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        # Extract MFCC features
        mfcc = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        
        # We want to have a unified size. We either pad or truncate.
        pad_width = max_pad_len - mfcc.shape[1]
        
        if pad_width > 0:
            # Need to pad the sequence
            mfcc = np.pad(mfcc, pad_width=((0, 0), (0, pad_width)), mode='constant')
        else:
            # Need to truncate the sequence
            mfcc = mfcc[:, :max_pad_len]
            
        return mfcc.flatten()
        
    except Exception as e:
        print(f"Error during feature extraction: {e}")
        return None
