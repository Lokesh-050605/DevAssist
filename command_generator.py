import google.generativeai as genai
from utils import extract_command

def generate_command(user_input):
    """Uses Gemini AI to convert natural language input into a valid Windows terminal command."""
    
    prompt = f"""
    Convert the following natural language instruction into a valid Windows terminal command.
    If it is a common action, return only the command without explanation.
    The target system is Windows 10.

    Instruction: {user_input}
    Command:
    """

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    if not response or not response.text:
        return "ERROR: No response from AI."

    return extract_command(response.text)
