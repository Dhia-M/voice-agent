import sounddevice as sd
import numpy as np

print("Available devices:")
print(sd.query_devices())

print("\nTesting default input...")
try:
    duration = 3  # seconds
    sample_rate = 16000
    sd.default.device = 3 
    
    # Record audio
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16', device=3)
    sd.wait()
    
    # Check if audio is silent
    volume = np.abs(audio).mean()
    print(f"Average volume: {volume}")
    
    if volume < 50:
        print("⚠️ TOO QUIET - Check mic permissions or device selection")
    else:
        print("✅ Mic is working!")
        
except Exception as e:
    print(f"❌ Microphone error: {e}")