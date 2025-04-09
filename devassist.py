import threading
import speech_recognition as sr
import queue
from command_processor import process_command
from utils import speak, stop_speaking

wake_word = "listen assistant"
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Queue for communication between threads
input_queue = queue.Queue()

# Events to control threads
stop_event = threading.Event()
pause_listening_event = threading.Event()

def listen_for_voice_command():
    """Continuously listens for wake word and subsequent commands."""
    while not stop_event.is_set():
        if not pause_listening_event.is_set():
            print("Opening microphone...")
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Listening for wake word...")
                try:
                    audio = recognizer.listen(source, timeout=5)
                    voice_input = recognizer.recognize_google(audio).lower()
                    print(f"Detected: {voice_input}")
                    if wake_word in voice_input:
                        speak("Yes, I'm listening...")
                        print("Yes, I'm listening...")
                        print("Adjusting for command...")
                        recognizer.adjust_for_ambient_noise(source, duration=1)
                        print("Listening for command...")
                        audio = recognizer.listen(source, timeout=10)
                        command = recognizer.recognize_google(audio).lower()
                        print(f"Voice command received: {command}")
                        input_queue.put(("voice", command))
                except sr.WaitTimeoutError:
                    print("Timeout waiting for wake word")
                    continue
                except sr.UnknownValueError:
                    speak("Sorry, I didn’t catch that.")
                    print("Couldn’t understand audio.")
                except sr.RequestError as e:
                    speak("There’s an issue with the speech service.")
                    print(f"Speech service error: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    speak("Something went wrong, please try again.")
        else:
            threading.Event().wait(0.1)

def listen_for_keyboard_input():
    """Listens for keyboard input in a non-blocking way."""
    while not stop_event.is_set():
        if not pause_listening_event.is_set():
            try:
                cmd = input(">> ")
                if cmd.strip():
                    print(f"Keyboard command received: {cmd}")
                    input_queue.put(("keyboard", cmd))
            except EOFError:
                print("Keyboard input closed.")
                break
        else:
            threading.Event().wait(0.1)

def process_inputs():
    """Processes inputs from the queue and manages listening state."""
    voice_thread = threading.Thread(target=listen_for_voice_command, daemon=True)
    keyboard_thread = threading.Thread(target=listen_for_keyboard_input, daemon=True)

    voice_thread.start()
    keyboard_thread.start()

    print(">> (Say 'Listen Assistant' or type a command, press Enter to submit.)")

    while not stop_event.is_set():
        try:
            input_type, cmd = input_queue.get(timeout=1)
            print(f"Processing {input_type} input: {cmd}")
            
            # Pause listening while processing
            pause_listening_event.set()
            speak("Processing your command...")
            
            if cmd.lower() == "exit":
                stop_event.set()
                speak("Goodbye.")
                print("Exiting program...")
                break
            
            process_command(cmd)
            speak("Command completed.")
            
            # Resume listening after processing
            pause_listening_event.clear()
            print(">> Listening again...")
            
            input_queue.task_done()
        except queue.Empty:
            continue

def main():
    """Main entry point."""
    try:
        process_inputs()
    finally:
        stop_event.set()
        stop_speaking()  # Cleanly stop TTS engine

if __name__ == "__main__":
    main()