import speech_recognition as sr
import queue
import threading
from speech import speak, stop_speech

# Queue for user input
input_queue = queue.Queue()

def handle_user_input(process_command):
    """Handles both voice and text input simultaneously."""
    recognizer = sr.Recognizer()
    
    while True:
        print("\nSelect Input Mode:\n[1] Voice Input\n[2] Text Input\n[3] Exit")
        speak("Select input mode. Press 1 for voice input, 2 for text input, or 3 to exit.")

        text_thread = threading.Thread(target=capture_text_input, daemon=True)
        voice_thread = threading.Thread(target=capture_voice_input, args=(recognizer,), daemon=True)
        
        text_thread.start()
        voice_thread.start()

        text_thread.join()
        voice_thread.join()

        user_input = input_queue.get() if not input_queue.empty() else None  # Get input from queue

        if user_input:
            print(f"Processing Command: {user_input}")
            speak(f"You said: {user_input}")  # Read aloud user input
            process_command(user_input)

        if user_input in ["exit", "quit", "3"]:
            print("Exiting DevAssist...")
            speak("Exiting DevAssist...")
            break

def capture_text_input():
    """Captures text input without blocking voice input."""
    user_input = input("Enter command: ").strip().lower()
    input_queue.put(user_input)

def capture_voice_input(recognizer):
    """Captures voice input without blocking text input."""
    with sr.Microphone() as source:
        try:
            stop_speech.set()  # Stop assistant speech immediately if user starts talking
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"Recognized Voice Input: {command}")
            input_queue.put(command)
        except sr.UnknownValueError:
            print("Sorry, could not understand the audio.")
            speak("Sorry, could not understand the audio.")
        except sr.RequestError:
            print("Could not request results from Google STT.")
            speak("Could not request results from Google STT.")
