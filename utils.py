def extract_command(response_text):
    """Extracts the terminal command from Gemini AI response."""
    lines = response_text.strip().split("\n")
    for line in lines:
        if "Command:" in line:
            return line.replace("Command:", "").strip()
    return lines[0]  # Fallback to first line if "Command:" is missing
