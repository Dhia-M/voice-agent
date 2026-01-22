import sounddevice as sd
import numpy as np

print("Testing speaker output...")

# Generate a simple tone
duration = 2  # seconds
frequency = 440  # Hz
sample_rate = 16000

t = np.linspace(0, duration, int(sample_rate * duration), False)
tone = np.sin(2 * np.pi * frequency * t) * 0.3

print(f"Playing tone on device 5...")
sd.play(tone, samplerate=sample_rate, device=5)
sd.wait()
print("✓ Tone played successfully!")