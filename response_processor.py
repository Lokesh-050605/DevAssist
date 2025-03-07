import subprocess
import json
import pyttsx3  # For text-to-speech (TTS)
import os

def speak(text):
    """Converts text to speech."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def execute_command(command):
    """Executes a terminal command and returns its output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout.strip() if result.stdout else result.stderr.strip()
    except Exception as e:
        return f"Error executing command: {str(e)}"

def read_file(file_path):
    """Reads the content of a given file."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return f"Error: File '{file_path}' not found."

def process_response(classification_result, gemini_response):
    """
    Processes the response from Gemini and takes the necessary action.
    - Reads aloud general queries.
    - Executes terminal commands and displays output.
    - Provides debugging solutions.
    - Handles file queries.
    """

    query_class = classification_result.get("class", "None")

    if query_class == "general_query":
        # Read aloud the response
        response_text = gemini_response.get("general_response", "No response available.")
        print("💬 Assistant:", response_text)
        speak(response_text)
        return response_text

    elif query_class == "terminal_command":
        commands = gemini_response.get("commands", [])
        command_outputs = []

        for cmd in commands:
            command_text = cmd["command"]
            description = cmd["description"]
            print(f"\n🔹 Executing: {command_text}\n   📌 {description}")
            output = execute_command(command_text)
            print(f"🖥️ Output:\n{output}")
            command_outputs.append({"command": command_text, "output": output})

        return {"executed_commands": command_outputs}

    elif query_class == "debugging":
        suggestions = gemini_response.get("debugging_suggestions", "No debugging steps provided.")
        print("🐞 Debugging Suggestions:")
        print(suggestions)
        return {"debugging_suggestions": suggestions}

    elif query_class == "file_query":
        file_name = gemini_response.get("file_name", "")
        file_content = gemini_response.get("file_content", "")

        if file_name and not file_content:
            file_content = read_file(file_name)

        print(f"📄 File Content ({file_name}):\n{file_content}")
        return {"file_name": file_name, "file_content": file_content}

    else:
        print("⚠️ Unrecognized query class.")
        return {"error": "Unknown query classification."}

# Example usage
from query_generator import classify_query
from query_gemini import query_gemini

user_input = "push changes to git"
classification_result = classify_query(user_input)
gemini_response = query_gemini(user_input)

process_response(classification_result, gemini_response)