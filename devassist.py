import threading
import speech_recognition as sr
import queue
from utils import speak, stop_speaking
import time
from command_processor import process_command


# If you have your own processor, replace filler with process_command
def filler(cmd):
    print(f"Simulating processing of command: {cmd}")
    time.sleep(5)
    print("Processing complete.")

# Shared components
wake_word = "listen assistant"
recognizer = sr.Recognizer()
input_queue = queue.Queue()
stop_event = threading.Event()
input_received = threading.Event()
filename = ""
file_handler = None

def listen_for_voice_command():
    microphone = sr.Microphone()
    while not stop_event.is_set():
        if input_received.is_set():
            time.sleep(0.5)
            continue

        print("Opening microphone...")
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Listening for wake word (say 'listen assistant')...")

                while not stop_event.is_set() and not input_received.is_set():
                    try:
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        voice_input = recognizer.recognize_google(audio).lower()
                        print(f"Detected: {voice_input}")
                        if wake_word in voice_input:
                            speak("Yes, I'm listening...")
                            print("Yes, I'm listening...")
                            break
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
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

                if input_received.is_set():
                    continue

                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening for command (10 sec timeout)...")
                try:
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"Voice command received: {command}")
                    input_queue.put(("voice", command))
                    input_received.set()
                except sr.WaitTimeoutError:
                    print("No command received within 10 seconds.")
                    speak("I didn’t hear a command, listening again.")
                except sr.UnknownValueError:
                    print("Couldn’t understand command.")
                    speak("Sorry, I couldn’t understand that.")
                except sr.RequestError as e:
                    print(f"Speech service error: {e}")
                    speak("There’s an issue with the speech service.")
                except Exception as e:
                    print(f"Unexpected error during command detection: {e}")
                    speak("Something went wrong.")
        except Exception as e:
            print(f"Microphone initialization error: {e}")
            speak("Failed to initialize microphone, please check your setup.")
        time.sleep(0.1)

def listen_for_keyboard_input():
    # print("Listening for keyboard input...")
    while not stop_event.is_set():
        if input_received.is_set():
            time.sleep(0.5)
            continue
        try:
            # print("enter...>>..")
            cmd = input(">>")
            if cmd.strip():
                print(f"Keyboard command received: {cmd}")
                input_queue.put(("keyboard", cmd))
                input_received.set()
        except EOFError:
            print("Keyboard input closed.")
            break
        except Exception as e:
            print(f"Keyboard error: {e}")
        time.sleep(0.1)

def process_inputs(process_func):
    global filename
    global file_handler
    
    print(">> (Say 'Listen Assistant' or type a command...)")

    voice_thread = threading.Thread(target=listen_for_voice_command, daemon=True)
    keyboard_thread = threading.Thread(target=listen_for_keyboard_input, daemon=True)

    voice_thread.start()
    keyboard_thread.start()

    while not stop_event.is_set():
        try:
            # print("filename:", filename)
            input_type, cmd = input_queue.get()
            print(f"Processing {input_type} input: {cmd}")

            speak("Processing your command...")

            if cmd.lower() == "exit":
                speak("Goodbye.")
                print("Exiting program...")
                break
            
            elif cmd.lower() == "done" or cmd.lower() == "close":
                if file_handler is None:
                    speak("No file is currently open.")
                    print("No file is currently open.")
                    input_received.clear()
                    continue
                print(f"File handler to be closed: {file_handler}")
                if file_handler:
                    file_handler.stop_nvim()
                    file_handler = None
                filename = ""
                print("File closed.")
                speak("File closed.")
                input_received.clear()
                continue

            res = process_func(cmd, filename)
            if res.get("filename", None) is not None:
                filename = res.get("filename")
            if res.get("file_handler", None) is not None:
                file_handler = res["file_handler"]
            speak("Command completed.")
            input_received.clear()
            print(">> Listening again...")
        except Exception as e:
            print(f"Error while processing: {e}")
            input_received.clear()

def main():
    try:
        process_inputs(process_command)
    finally:
        stop_event.set()
        stop_speaking()
        if file_handler:
            file_handler.stop_nvim()

if __name__ == "__main__":
    main()
