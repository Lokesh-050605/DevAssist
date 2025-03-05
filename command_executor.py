import os
import subprocess
import pyttsx3

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    """Speaks the provided text for accessibility."""
    if text:  # Avoid speaking empty text
        engine.say(text)
        engine.runAndWait()

def execute_command(command):
    """
    Executes the generated Windows/Linux/Mac terminal command.
    Provides audio feedback for visually impaired programmers.
    """
    try:
        print(f"Executing: {command}")
        speak(f"Executing: {command}")

        stdout, stderr = "", ""  # Ensure stdout and stderr are always initialized

        if "nvim" in command:  # Handle Neovim separately
            process = subprocess.Popen(command, shell=True)  # Open Neovim without blocking
        else:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            try:
                stdout, stderr = process.communicate(timeout=10)  # Prevent hanging
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = "", "ERROR: Command execution timed out."

        if stdout.strip():  # Only print if there's actual output
            print(f"Output:\n{stdout}")
            speak(stdout[:100])  # Read only first 100 characters

        if stderr.strip():  # Print only if there's an actual error
            print(f"Error:\n{stderr}")
            speak("An error occurred while executing the command.")

    except Exception as e:
        print(f"ERROR: Failed to execute command - {e}")
        speak("Failed to execute the command.")

if __name__ == "__main__":
    test_command = "echo Hello, Dev Assist!"
    execute_command(test_command)
