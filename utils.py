import json
import pyttsx3
import subprocess
import os

def speak(text):
    """Converts text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def extract_command(response_text):
    """
    Extracts the exact terminal command from AI response.
    Cleans unnecessary text and ensures correctness.
    """
    if not response_text or not isinstance(response_text, str):
        return "ERROR: Invalid input."

    lines = response_text.strip().split("\n")

    # Check for explicitly marked command
    for line in lines:
        if "Command:" in line:
            return line.split("Command:", 1)[-1].strip()

    # Remove Markdown-style code blocks
    cleaned_lines = [line.strip() for line in lines if not line.startswith("```")]

    # Return the last non-empty line as command
    command = cleaned_lines[-1] if cleaned_lines else ""

    return command if command else "ERROR: No command found."

def load_user_config(filepath="user_config.json"):
    """Loads user configuration from a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
def execute_command(command):
    """Executes a terminal command and returns its output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except Exception as e:
        return f"Error executing command: {str(e)}"

