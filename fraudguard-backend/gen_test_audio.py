import numpy as np
import wave
import struct

# Generate 3 seconds of 440Hz tone as a test wav
sr, duration, freq = 44100, 3, 440
t = np.linspace(0, duration, int(sr * duration))
audio = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)

with wave.open('test_audio.wav', 'w') as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(sr)
    f.writeframes(struct.pack('<' + 'h'*len(audio), *audio))
print('test_audio.wav created')
