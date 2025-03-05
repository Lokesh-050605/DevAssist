from speech import speak

def process_command(command):
    """Processes the user command and speaks the response."""
    response = f"Executing command: {command}"  # Dummy processing
    print(response)
    speak(response)
