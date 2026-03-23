import librosa
import numpy as np
try:
    y, sr = librosa.load('test_audio.wav', sr=None)
    print("Librosa load success")
except Exception as e:
    print(f"Librosa load failed: {e}")

import whisper
try:
    model = whisper.load_model("base")
    print("Whisper model load success")
    print("Attempting transcription (this requires ffmpeg)...")
    res = model.transcribe('test_audio.wav')
    print(f"Transcription success: {res['text']}")
except Exception as e:
    print(f"Transcription failed: {e}")
