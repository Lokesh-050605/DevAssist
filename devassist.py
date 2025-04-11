import threading
import speech_recognition as sr
import queue
from command_processor import process_command
from utils import speak, stop_speaking

wake_word = "listen assistant"
recognizer = sr.Recognizer()

input_queue = queue.Queue()
stop_event = threading.Event()

def listen_for_voice_command():
    microphone = sr.Microphone()
    while not stop_event.is_set():
        print("Opening microphone...")
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Listening for wake word (say 'listen assistant')...")
                while True:
                    try:
                        audio = recognizer.listen(source)
                        voice_input = recognizer.recognize_google(audio).lower()
                        print(f"Detected: {voice_input}")
                        if wake_word in voice_input:
                            speak("Yes, I'm listening...")
                            print("Yes, I'm listening...")
                            break
                    except sr.UnknownValueError:
                        # print("Couldn’t understand audio, still listening...")
                        print("...")
                        continue
                    except sr.RequestError as e:
                        print(f"Speech service error: {e}")
                        speak("There’s an issue with the speech service.")
                        return
                    except Exception as e:
                        print(f"Unexpected error during wake word detection: {e}")
                        speak("Something went wrong, please try again.")
                        return

                print("Adjusting for command...")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening for command (10 sec timeout)...")
                try:
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Voice command received: {command}")
                    input_queue.put(("voice", command))
                    return
                except sr.WaitTimeoutError:
                    print("No command received within 10 seconds, returning to wake word...")
                    speak("I didn’t hear a command, listening for wake word again...")
                    return
                except sr.UnknownValueError:
                    print("Couldn’t understand command, returning to wake word...")
                    speak("Sorry, I couldn’t understand that, listening for wake word again...")
                    return
                except sr.RequestError as e:
                    print(f"Speech service error during command: {e}")
                    speak("There’s an issue with the speech service.")
                    return
                except Exception as e:
                    print(f"Unexpected error during command detection: {e}")
                    speak("Something went wrong, please try again.")
                    return

        except Exception as e:
            print(f"Microphone initialization error: {e}")
            speak("Failed to initialize microphone, please check your audio setup.")
            return
        threading.Event().wait(0.1)

def listen_for_keyboard_input():
    while not stop_event.is_set():
        try:
            cmd = input(">> ")
            if cmd.strip():
                print(f"Keyboard command received: {cmd}")
                input_queue.put(("keyboard", cmd))
                return
        except EOFError:
            print("Keyboard input closed.")
            break
        threading.Event().wait(0.1)

def process_inputs():
    print(">> (Say 'Listen Assistant' or type a command, press Enter to submit.)")

    while not stop_event.is_set():
        # Start listening threads
        voice_thread = threading.Thread(target=listen_for_voice_command, daemon=True)
        keyboard_thread = threading.Thread(target=listen_for_keyboard_input, daemon=True)

        voice_thread.start()
        keyboard_thread.start()

        try:
            input_type, cmd = input_queue.get()  # No timeout, wait indefinitely
            print(f"Processing {input_type} input: {cmd}")
            
            # Stop threads after input received
            stop_event.set()
            voice_thread.join(timeout=1)
            keyboard_thread.join(timeout=1)
            stop_event.clear()

            speak("Processing your command...")
            
            if cmd.lower() == "exit":
                speak("Goodbye.")
                print("Exiting program...")
                break
            
            process_command(cmd)
            speak("Command completed.")
            
            print(">> Listening again...")
            input_queue.task_done()

        except queue.Empty:  # This won’t trigger without timeout
            print("Unexpected queue empty error, restarting...")
            stop_event.set()
            voice_thread.join(timeout=1)
            keyboard_thread.join(timeout=1)
            stop_event.clear()

def main():
    try:
        process_inputs()
    finally:
        stop_event.set()
        stop_speaking()

if __name__ == "__main__":
    main()