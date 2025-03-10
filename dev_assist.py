import threading
import queue
from speech import speak, speech_worker, exit_event, stop_speech, listen_for_wake_word


# Queue to store user input (from voice or text)
input_queue = queue.Queue()


if __name__ == "__main__":
    print("[Starting DevAssist]: AI-powered coding assistant for blind developers.")

    # Start the speech worker in a separate thread
    speech_thread = threading.Thread(target=speech_worker, daemon=True)
    speech_thread.start()

    # Listen for wake word before processing commands
    listen_for_wake_word()

    # Ensure threads stay alive
    speech_thread.join()
