import subprocess
import re
import time
import os
import select
import queue

def execute_command(command):
    """
    Execute a terminal command using subprocess.Popen with non-blocking polling.
    Returns a dict with success status, output, error, and command.
    """
    try:
        # Set environment for unbuffered Python output
        env = os.environ.copy()
        if command.startswith("python"):
            env["PYTHONUNBUFFERED"] = "1"
            command = f"python -u {command[7:]}"  # Force unbuffered with -u

        # Start the subprocess
        process = subprocess.Popen(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            env=env
        )
        output_lines = []
        error_lines = []
        start_time = time.time()
        stdout_queue = queue.Queue()
        stderr_queue = queue.Queue()

        def read_nonblocking(pipe, q):
            """Read available data from pipe into queue."""
            while True:
                try:
                    # Use select to check if data is available (0.1s timeout)
                    readable, _, _ = select.select([pipe], [], [], 0.1)
                    if pipe in readable:
                        line = pipe.readline().strip()
                        if line:
                            q.put(line)
                    else:
                        break
                except ValueError:
                    break  # Pipe closed

        while process.poll() is None and time.time() - start_time < 15:
            # Read stdout non-blocking
            read_nonblocking(process.stdout, stdout_queue)
            try:
                while True:
                    line = stdout_queue.get_nowait()
                    output_lines.append(line)
                    print(line)
                    speak(line)
                    if is_prompt(line):
                        print(f"{line} ", end="", flush=True)
                        speak(f"Prompt: {line}")
                        user_input = input()
                        process.stdin.write(user_input + "\n")
                        process.stdin.flush()
                        output_lines.append(f"[User Input]: {user_input}")
                    else:
                        print(f"[Output]: {line}")
            except queue.Empty:
                pass

            # Read stderr non-blocking
            read_nonblocking(process.stderr, stderr_queue)
            try:
                while True:
                    line = stderr_queue.get_nowait()
                    error_lines.append(line)
                    print(f"Error: {line}")
                    speak(f"Error: {line}")
                    print(f"[Error]: {line}")
            except queue.Empty:
                pass

            time.sleep(0.005)

        # Collect remaining output
        read_nonblocking(process.stdout, stdout_queue)
        read_nonblocking(process.stderr, stderr_queue)
        try:
            while True:
                line = stdout_queue.get_nowait()
                output_lines.append(line)
                print(line)
                speak(line)
                print(f"[Final Output]: {line}")
        except queue.Empty:
            pass
        try:
            while True:
                line = stderr_queue.get_nowait()
                error_lines.append(line)
                print(f"Error: {line}")
                speak(f"Error: {line}")
                print(f"[Final Error]: {line}")
        except queue.Empty:
            pass

        # Clean up
        process.stdout.close()
        process.stderr.close()
        process.stdin.close()

        # Handle timeout
        if time.time() - start_time >= 15:
            process.terminate()
            error_lines.append("Command timed out after 15 seconds")
            return {
                "success": False,
                "error": "\n".join(error_lines),
                "output": "\n".join(output_lines),
                "command": command
            }

        return {
            "success": process.returncode == 0,
            "output": "\n".join(output_lines),
            "error": "\n".join(error_lines),
            "command": command
        }

    except Exception as e:
        print(f"Execution failed: {str(e)}")
        speak(f"Execution failed: {str(e)}")
        return {
            "success": False,
            "error": f"Execution failed: {str(e)}",
            "command": command
        }

def is_prompt(line):
    """
    Detect if a line is an interactive prompt.
    """
    line = line.lower().strip()
    prompt_indicators = [
        r":$",            # Ends with : (e.g., Enter your name:)
        r"\?$",           # Ends with ? (e.g., Proceed?)
        r"\[y/n\]",       # e.g., Proceed [y/n]
        r"enter.*name",   # e.g., Enter your name:
        r"enter.*age"     # e.g., Enter your age:
    ]
    return any(re.search(pattern, line) for pattern in prompt_indicators)

def speak(text):
    """
    Placeholder for your speak function.
    """
    print(f"[SPEAK]: {text}")

def test_commands():
    """
    Test harness for various commands.
    """
    test_cases = [
        "dir",
        'python -c "import sys; sys.stdout.write(input(\'Enter name: \')); sys.stdout.flush()"',
        "python test.py",
        # Uncomment to test installation
        # "pip install requests",
    ]

    for cmd in test_cases:
        print(f"\n=== Testing Command: {cmd} ===")
        result = execute_command(cmd)
        print("\nResult:")
        print(f"Success: {result['success']}")
        if result["success"]:
            print(f"Output: {result['output']}")
        else:
            print(f"Error: {result['error']}")
        print("===")

if __name__ == "__main__":
    test_commands()