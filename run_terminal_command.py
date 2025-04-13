import subprocess
import threading
import sys
import pyttsx3
from utils import speak

# This will hold events for each speech task
speech_threads = []

def read_output(process):
    buffer = ""
    while True:
        char = process.stdout.read(1)
        if not char:
            break
        buffer += char
        sys.stdout.write(char)
        sys.stdout.flush()

        if char == '\n':
            line = buffer.strip()
            if line:
                # Thread for speaking, add to speech_threads for synchronization
                speak_thread = threading.Thread(target=speak, args=(line,))
                speech_threads.append(speak_thread)
                speak_thread.start()
            buffer = ""
        elif buffer.endswith(": "):
            # Handle prompt line
            speak_thread = threading.Thread(target=speak, args=(buffer.strip(),))
            speech_threads.append(speak_thread)
            speak_thread.start()

def input_loop(process):
    try:
        while process.poll() is None:
            user_input = input()
            if process.poll() is not None:
                break
            if process.stdin and not process.stdin.closed:
                process.stdin.write(user_input + "\n")
                process.stdin.flush()
    except EOFError:
        pass
    except KeyboardInterrupt:
        print("\nStopped by user")

# Start the subprocess
def execute_command(command):
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,  # Capturing stderr separately
        text=True,
        bufsize=1
    )

    # Start reading output
    output_thread = threading.Thread(target=read_output, args=(process,))
    output_thread.daemon = True
    output_thread.start()

    # Start input handling
    input_thread = threading.Thread(target=input_loop, args=(process,))
    input_thread.daemon = True
    input_thread.start()

    # Wait for process to finish
    process.wait()

    # Wait for all speech threads to finish before terminating
    for t in speech_threads:
        t.join()

    # Cleanup
    try:
        if process.stdin and not process.stdin.closed:
            process.stdin.close()
    except OSError:
        pass

    output_thread.join(timeout=1)
    input_thread.join(timeout=1)

    # Check for errors
    if process.returncode != 0:
        # Capture stderr output
        error_output = process.stderr.read().strip()
        return {"success": False, "error": error_output, "command": command}

    # If no errors, return success and output
    return {"success": True, "output": process.stdout.read().strip()}

    print("\n✅ Subprocess finished and exited cleanly.")
