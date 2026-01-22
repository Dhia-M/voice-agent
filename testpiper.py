from piper.voice import PiperVoice
import io
import numpy as np

print("Testing Piper with detailed debug...")

try:
    # Load model
    tts = PiperVoice.load(r"C:\voice_models\en_US-amy-low.onnx")
    print("✓ Model loaded")
    
    # Test synthesis step by step
    text = "Hello world"
    audio_buffer = io.BytesIO()
    
    print(f"Synthesizing: '{text}'")
    tts.synthesize(text, audio_buffer)
    
    size = audio_buffer.tell()
    print(f"Buffer position: {size}")
    
    if size == 0:
        print("❌ Piper wrote nothing! Trying alternative text...")
        
        # Try simpler text
        audio_buffer = io.BytesIO()
        tts.synthesize("A", audio_buffer)
        print(f"Single char test: {audio_buffer.tell()} bytes")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()