import subprocess
import threading
import sys
from utils import speak

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

def execute_command(command):
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, 
        text=True,
        bufsize=1,
        shell=True,
    )

    # Start reading output
    output_thread = threading.Thread(target=read_output, args=(process,))
    output_thread.daemon = True
    output_thread.start()

    # Start input handling
    input_thread = threading.Thread(target=input_loop, args=(process,))
    input_thread.daemon = True
    input_thread.start()

    process.wait()

    for t in speech_threads:
        t.join()

    try:
        if process.stdin and not process.stdin.closed:
            process.stdin.close()
    except OSError:
        pass

    output_thread.join(timeout=1)
    input_thread.join(timeout=1)

    # Check for errors
    if process.returncode != 0:
        error_output = process.stderr.read().strip()
        return {"success": False, "error": error_output, "command": command}
    return {"success": True, "output": process.stdout.read().strip()}

# print(execute_command("cd"))
