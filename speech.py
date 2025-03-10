import speech_recognition as sr
import pyttsx3
import queue
import threading

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
speech_queue = queue.Queue()
exit_event = threading.Event()
stop_speech = threading.Event()

def speech_worker():
    """Thread function to process speech requests sequentially."""
    while not exit_event.is_set():
        try:
            text = speech_queue.get(timeout=1)
            if stop_speech.is_set():
                continue  # Skip speaking if user is typing
            print(f"[Assistant]: {text}")  
            engine.say(text)
            engine.runAndWait()
            speech_queue.task_done()
        except queue.Empty:
            continue  # No pending speech requests

def speak(text):
    """Add text to the speech queue for processing."""
    speech_queue.put(text)

def listen_for_wake_word(callback):
    """Listens for the wake word 'Dev' or allows typing."""
    recognizer = sr.Recognizer()
    print("[Listening]: Waiting for 'Dev' wake word...")
    speak("Listening for wake word Dev")

    while not exit_event.is_set():
        with sr.Microphone() as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()

                if "dev" in command:
                    print("[Wake Word Detected]: Processing command...")
                    speak("Wake word detected. Please say your command.")
                    callback()
                    break
            except sr.UnknownValueError:
                pass  
            except sr.RequestError:
                print("[Error]: Speech Recognition service error.")
                speak("Speech Recognition service error.")

        # Allow user to type the wake word
        user_input = input("[Type 'Dev' to activate]: ").strip().lower()
        if user_input == "dev":
            print("[Wake Word Detected]: Processing command...")
            speak("Wake word detected. Please say your command.")
            callback()
            break
