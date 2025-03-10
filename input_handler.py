import speech_recognition as sr
import queue
import threading
from speech import speak, stop_speech, exit_event
from command_processor import process_command

input_queue = queue.Queue()

def handle_user_input():
    """Handles both voice and text input in parallel."""
    recognizer = sr.Recognizer()

    # Start voice & text input in separate threads
    voice_thread = threading.Thread(target=capture_voice_input, args=(recognizer,), daemon=True)
    text_thread = threading.Thread(target=capture_text_input, daemon=True)

    voice_thread.start()
    text_thread.start()

    # Keep processing input continuously
    while not exit_event.is_set():
        user_input = input_queue.get() if not input_queue.empty() else None

        if user_input:
            print(f"[Processing Command]: {user_input}")
            speak(f"Processing command: {user_input}")
            process_command(user_input)  # Send command for processing

        if user_input in ["exit", "quit"]:
            print("[Shutting Down]: DevAssist is closing...")
            speak("Shutting down DevAssist.")
            exit_event.set()
            break

    # Stop all input threads before exiting
    voice_thread.join()
    text_thread.join()

def capture_text_input():
    """Captures text input and pauses voice recognition while typing."""
    global stop_speech
    while not exit_event.is_set():
        user_input = input("[Type Command]: ").strip().lower()
        if user_input:
            stop_speech.set()  # Pause speech recognition
            input_queue.put(user_input)
            stop_speech.clear()  # Resume speech recognition after typing is done

def capture_voice_input(recognizer):
    """Captures voice input and adds it to the input queue."""
    max_retries = 3  # Max retries before skipping
    
    while not exit_event.is_set():
        retries = 0
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.dynamic_energy_threshold = True  # Auto adjust for background noise

            while retries < max_retries:
                try:
                    if stop_speech.is_set():
                        continue  # Skip if typing is happening

                    print("[Listening for voice input]...")
                    audio = recognizer.listen(source, timeout=5)

                    command = recognizer.recognize_google(audio).lower()
                    print(f"[Recognized Voice Input]: {command}")
                    input_queue.put(command)
                    break  # Successfully recognized, break retry loop

                except sr.UnknownValueError:
                    print(f"[Error]: Could not understand speech. Retry {retries + 1}/{max_retries}")
                    speak("Sorry, I could not understand that.")
                    retries += 1
                except sr.RequestError:
                    print("[Error]: Speech recognition service unavailable.")
                    speak("Speech recognition service unavailable.")
                    break  # Don't retry if service is down
                except sr.WaitTimeoutError:
                    print("[Timeout]: No speech detected.")
                    break  # Stop retrying if no input is detected