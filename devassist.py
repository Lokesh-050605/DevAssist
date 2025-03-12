import threading
import speech_recognition as sr
import queue
import time
from command_processor import process_command
from utils import speak



wake_word = "listen assistant"  # Define the wake-up word
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Queue for communication between threads
input_queue = queue.Queue()

# Lock to manage microphone access
mic_lock = threading.Lock()

# Flags to control the threads
voice_thread_active = True
keyboard_thread_active = True

def listen_for_voice_command():
    """Listens for the voice command after detecting the wake word."""
    global voice_thread_active
    while voice_thread_active:
        with mic_lock:  # Lock the microphone resource
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
                try:
                    #print("Listening for wake word...")
                    audio = recognizer.listen(source)  # Timeout for wake word detection
                    voice_command = recognizer.recognize_google(audio).lower()
                    #print(f"Voice command received: {voice_command}")
                    if wake_word in voice_command:
                        print("Yes, I'm listening....")
                        speak("Yes, I'm listening.")
                        audio = recognizer.listen(source) 
                        voice_command = recognizer.recognize_google(audio).lower()
                        print(f"Command received: {voice_command}")
                        input_queue.put(("voice", voice_command)) # Put command in queue
                except sr.WaitTimeoutError:
                    print("No voice input detected within the timeout period.")
                except sr.UnknownValueError:
                    print("")

                except sr.RequestError as e:
                    print(f"Could not request results; {e}")
          # Small delay to avoid busy-waiting

def listen_for_keyboard_input():
    """Listens for keyboard input and puts it into the queue."""
    global keyboard_thread_active
    try:
        while keyboard_thread_active:
            cmd = input(">> ")
            input_queue.put(("keyboard", cmd))  # Put command in queue
    except EOFError:
        print("Keyboard input closed.")

def input_dual():
    """Handles both voice and keyboard input in parallel."""
    global voice_thread_active, keyboard_thread_active

    # Start the voice and keyboard threads
    voice_thread = threading.Thread(target=listen_for_voice_command, daemon=True)
    keyboard_thread = threading.Thread(target=listen_for_keyboard_input, daemon=True)
    
    voice_thread.start()
    keyboard_thread.start()

    # Wait for the first input from either thread
    print(">> (You can say 'Listen Assistant' or type a command.)")
    
    while True:
        if not input_queue.empty():
            input_type, cmd = input_queue.get()
            input_queue.queue.clear()  # Clear the queue after processing
            print(f"Received {input_type} input: {cmd}")

            # Signal threads to stop
            voice_thread_active = False
            keyboard_thread_active = False

            # Allow threads to finish gracefully
            voice_thread.join(timeout=1)  # Wait for the voice thread to release the lock
            keyboard_thread.join(timeout=1)  # Wait for the keyboard thread to finish

            return cmd

def main():
    """Main entry point for the program to process user commands."""
    global voice_thread_active, keyboard_thread_active
    while True:
        # Reset flags for the next cycle
        voice_thread_active = True
        keyboard_thread_active = True

        # Get input either from voice or keyboard
        cmd = input_dual()

        if cmd.lower() == "exit":
            print("Exiting program...")
            break

        process_command(cmd)  # Process the received command

if __name__ == "__main__":
    main()