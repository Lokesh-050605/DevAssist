import speech_recognition as sr
import queue
import threading
from speech import speak, stop_speech, exit_event

input_queue = queue.Queue()

def handle_user_input(process_command):
    """Handles both voice and text input using separate threads."""
    recognizer = sr.Recognizer()

    while not exit_event.is_set():
        print("\n[Menu]: Choose input method")
        print("[1] Voice Input\n[2] Text Input\n[3] Exit")
        speak("Press 1 for voice input, 2 for text input, or 3 to exit.")

        text_thread = threading.Thread(target=capture_text_input, daemon=True)
        voice_thread = threading.Thread(target=capture_voice_input, args=(recognizer,), daemon=True)

        text_thread.start()
        voice_thread.start()

        text_thread.join()
        voice_thread.join()

        user_input = input_queue.get() if not input_queue.empty() else None

        if user_input:
            print(f"[Processing]: {user_input}")
            speak(f"You said: {user_input}")
            process_command(user_input)

        if user_input in ["exit", "quit", "3"]:
            print("[Exiting]: Shutting down DevAssist...")
            speak("Exiting DevAssist...")
            exit_event.set()
            break

def capture_text_input():
    """Captures text input and pauses voice recognition."""
    stop_speech.set()  
    user_input = input("[Type your command]: ").strip().lower()
    input_queue.put(user_input)
    stop_speech.clear()  

def capture_voice_input(recognizer):
    """Captures voice input while allowing text input."""
    with sr.Microphone() as source:
        try:
            stop_speech.set()  
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"[Voice Command]: {command}")
            input_queue.put(command)
        except sr.UnknownValueError:
            print("[Error]: Could not understand speech.")
            speak("Sorry, could not understand the audio.")
        except sr.RequestError:
            print("[Error]: Could not request results from Google STT.")
            speak("Could not request results from Google Speech Recognition.")
