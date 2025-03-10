from speech import speak

def process_command(command):
    """Processes user commands and provides appropriate responses."""
    command = command.lower()

    if command in ["hello", "hi"]:
        response = "Hello! How can I assist you today?"
    elif command in ["exit", "quit"]:
        response = "Goodbye! Exiting DevAssist."
    elif command in ["time"]:
        from datetime import datetime
        response = f"The current time is {datetime.now().strftime('%H:%M:%S')}"
    else:
        response = f"Sorry, I don't understand the command: {command}"

    print(f"[Assistant]: {response}")
    speak(response)
