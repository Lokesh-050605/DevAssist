import json
import pyttsx3
import subprocess


def speak(text):
    """Converts text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def execute_command(command):
    """Executes a terminal command and returns its output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"  # Return error as a string
    except Exception as e:
        return f"Execution failed: {str(e)}"


def load_user_config(filepath="user_config.json"):
    """Loads user configuration from a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
