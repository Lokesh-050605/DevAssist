import json
import pyttsx3
import subprocess
import threading

# Thread-safe engine initialization
engine_lock = threading.Lock()

def speak(text):
    """Synchronously speak the given text with thread-safe engine."""
    print(f"Speaking: {text}")
    with engine_lock:
        engine = pyttsx3.init()  # Fresh engine instance per call
        engine.say(text)
        engine.runAndWait()

def stop_speaking():
    """Stop any ongoing speech."""
    with engine_lock:
        engine = pyttsx3.init()
        engine.stop()

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip()}
        else:
            return {"success": False, "error": result.stderr.strip(), "command": command}
    except Exception as e:
        return {"success": False, "error": f"Execution failed: {str(e)}", "command": command}

def load_user_config(filepath="user_config.json"):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}