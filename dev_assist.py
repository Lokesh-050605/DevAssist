import speech_recognition as sr
import pyttsx3
import threading
import queue

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()
speech_queue = queue.Queue()  # Queue to manage speech requests
exit_event = threading.Event()  # Event to stop threads gracefully
stop_speech = threading.Event()  # Flag to stop speech if user starts speaking

# Queue for user input
input_queue = queue.Queue()

def speech_worker():
    """Thread function to process speech requests sequentially."""
    while not exit_event.is_set():
        try:
            text = speech_queue.get(timeout=1)
            if stop_speech.is_set():
                continue  # Skip speaking if user is speaking
            
            engine.say(text)
            engine.runAndWait()
            speech_queue.task_done()
        except queue.Empty:
            continue  # No pending speech requests

def speak(text):
    """Add text to the speech queue for processing."""
    speech_queue.put(text)

def listen_for_wake_word():
    """Continuously listens for the wake word 'Dev' and also allows typing."""
    recognizer = sr.Recognizer()
    print("Say 'Dev' to activate or type 'Dev' to start...")
    speak("Say Dev to activate or type Dev to start.")

    while not exit_event.is_set():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening for 'Dev'...")
            try:
                audio = recognizer.listen(source, timeout=5)
                command = recognizer.recognize_google(audio).lower()

                if "dev" in command:
                    print("Wake word detected! DevAssist is now active.")
                    speak("Wake word detected! DevAssist is now active.")
                    handle_user_input()
                    break
            except sr.UnknownValueError:
                pass  # Ignore and keep listening
            except sr.RequestError:
                print("Speech service error.")
            except sr.WaitTimeoutError:
                pass  # No speech detected, continue listening

        # Allow user to type wake word
        user_input = input("Type 'Dev' to activate: ").strip().lower()
        if user_input == "dev":
            print("Wake word detected! DevAssist is now active.")
            speak("Wake word detected! DevAssist is now active.")
            handle_user_input()
            break

def handle_user_input():
    """Handles both voice and text input simultaneously."""
    recognizer = sr.Recognizer()
    
    while not exit_event.is_set():
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
            exit_event.set()
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

def process_command(command):
    """Processes the user command and speaks the response."""
    response = f"Executing command: {command}"  # Dummy processing
    print(response)
    speak(response)

# Multi-Threading Implementation
if __name__ == "__main__":
    # Thread 1: Dedicated Speech Thread
    speech_thread = threading.Thread(target=speech_worker, daemon=True)
    speech_thread.start()

    # Thread 2: Wake Word Listener
    wake_word_thread = threading.Thread(target=listen_for_wake_word, daemon=True)
    wake_word_thread.start()

    # Keep the main program running
    wake_word_thread.join()
    speech_thread.join()
