import speech_recognition as sr

def test_speech_recognition():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Noise reduction
        print("🎤 Say something...")
        
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            print(f"✅ Recognized Speech: {command}")
        except sr.UnknownValueError:
            print("❌ Error: Could not understand speech.")
        except sr.RequestError:
            print("❌ Error: Speech recognition service unavailable.")
        except sr.WaitTimeoutError:
            print("⏳ Timeout: No speech detected.")

if __name__ == "__main__":
    test_speech_recognition()
