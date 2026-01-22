import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from openai import OpenAI
import wave
import io
import webrtcvad
import time
from vosk import Model, KaldiRecognizer
import json
import pyttsx3

class LMVoiceAgent:
    def __init__(self):
        # ASR - Vosk
        print("Loading Vosk ASR...")
        self.asr_model = Model(r"C:\voice_models\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15")
        self.asr_recognizer = KaldiRecognizer(self.asr_model, 16000)
        print("✓ Vosk loaded!")
        
        # LLM - LM Studio
        self.llm_client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="not-needed"
        )
        self.model_name = "yi-coder-9b-chat"
        
        # VAD - WebRTC
        self.vad = webrtcvad.Vad(3)
        
        # Audio settings
        self.sample_rate = 16000
        self.frame_duration = 30
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        
        print(f"Audio frame size: {self.frame_size}")
        
    def record_audio(self, max_duration=10):
        """Record audio from microphone"""
        print(f"\n🎤 Recording... (max {max_duration}s, speak clearly)")
        sd.default.device = 3  # Force Realtek mic
        
        audio_data = sd.rec(
            int(max_duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16',
            blocking=False,
            device=3
        )
        
        speech_detected = False
        silent_chunks = 0
        max_silent = 40
        
        for i in range(0, max_duration * 1000 // self.frame_duration):
            time.sleep(self.frame_duration / 1000)
            
            start_idx = i * self.frame_size
            end_idx = start_idx + self.frame_size
            
            if end_idx >= len(audio_data):
                break
            
            frame = audio_data[start_idx:end_idx].tobytes()
            
            try:
                if self.vad.is_speech(frame, self.sample_rate):
                    speech_detected = True
                    silent_chunks = 0
                elif speech_detected:
                    silent_chunks += 1
                    if silent_chunks > max_silent:
                        print("✓ Silence detected, stopping...")
                        break
            except:
                pass
        
        sd.stop()
        
        if not speech_detected:
            print("⚠️ No speech detected")
            return None
        
        end_idx = min((i + 1) * self.frame_size, len(audio_data))
        return audio_data[:end_idx]
    
    def transcribe(self, audio_data):
        """Transcribe audio to text"""
        print("[📝 Transcribing...]")
        
        if audio_data is None:
            return ""
        
        self.asr_recognizer.Reset()
        audio_bytes = audio_data.astype(np.int16).tobytes()
        chunk_size = 4000
        
        for i in range(0, len(audio_bytes), chunk_size):
            chunk = audio_bytes[i:i+chunk_size]
            self.asr_recognizer.AcceptWaveform(chunk)
        
        result = json.loads(self.asr_recognizer.FinalResult())
        text = result.get("text", "").strip()
        
        if text:
            print(f"👤 You: {text}")
        return text
    
    def get_llm_response(self, text):
        """Get response from LM Studio"""
        if not text:
            return ""
        
        print("[🤔 Thinking...]")
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": text}],
                temperature=0.7,
                max_tokens=512
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return "Sorry, I couldn't process that."
    
    def speak(self, text):
        """Speak text using pyttsx3 with Microsoft Zira voice"""
        if not text:
            print("⚠️ No text to speak")
            return
        
        print(f"🤖 Agent: {text}")
        print("[🔊 Speaking...]")
        
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            # Set Microsoft Zira voice explicitly
            zira_voice_id = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
            
            # Verify voice exists (optional - remove after confirming it works)
            voices = engine.getProperty('voices')
            voice_found = False
            for voice in voices:
                if voice.id == zira_voice_id:
                    engine.setProperty('voice', zira_voice_id)
                    voice_found = True
                    break
            
            if not voice_found:
                print("⚠️ Microsoft Zira voice not found, using default")
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            print("✓ Spoke successfully")
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
    
    def run(self):
        """Main conversation loop"""
        print("\n" + "="*40)
        print("🎮 LM Studio Voice Agent Ready!")
        print("Press Ctrl+C to exit")
        print("="*40 + "\n")
        
        while True:
            try:
                audio = self.record_audio(max_duration=5)
                text = self.transcribe(audio)
                response = self.get_llm_response(text)
                
                if response:
                    self.speak(response)
                
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    agent = LMVoiceAgent()
    agent.run()