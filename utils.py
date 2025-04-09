import json
import pyttsx3
import subprocess
import logging

# Setup logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

engine = pyttsx3.init()
engine.startLoop(False)  # Non-blocking mode

def speak(text):
    """Speaks the given text in non-blocking mode."""
    # logger.debug(f"Speaking: {text}")
    try:
        engine.say(text)
        # logger.debug("Text queued for speaking")
        engine.iterate()  # Process in main loop
        # logger.debug("Text spoken successfully")
    except Exception as e:
        print(f"Error speaking: {e}")

def stop_speaking():
    """Stops the TTS engine cleanly."""
    engine.endLoop()

def execute_command(command):
    """Executes a terminal command and returns its output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error: {result.stderr.strip()}"
    except Exception as e:
        return f"Execution failed: {str(e)}"

def load_user_config(filepath="user_config.json"):
    """Loads user configuration from a JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}