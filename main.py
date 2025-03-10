import threading
from speech import speech_worker, listen_for_wake_word, exit_event
from input_handler import handle_user_input
from command_processor import process_command

if __name__ == "__main__":
    # Start speech synthesis thread
    speech_thread = threading.Thread(target=speech_worker, daemon=True)
    speech_thread.start()

    # Start wake word detection
    listen_for_wake_word(lambda: handle_user_input(process_command))

    # Keep the program running
    speech_thread.join()
