# Description: This file contains the function to process the response from Gemini and take the necessary action.
import os
from interactive_debug import interactive_debugging
from utils import speak, execute_command


def read_file(file_path): 
    """Reads the content of a given file."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    return f"Error: File '{file_path}' not found."

def process_response(classification_result, gemini_response):
    """
    Processes the response from Gemini and takes the necessary action.
    """
    query_class = classification_result.get("class", "None")
    
    steps = []

    if query_class == "general_query":
        response_text = gemini_response.get("general_response", "No response available.")
        steps.append("Processing a general query.")
        steps.append("Speaking the response aloud.")
        speak("Processing a general query. Speaking the response aloud.")
        print("Assistant:", response_text)
        speak(response_text)
        return response_text

    elif query_class == "terminal_command":
        commands = gemini_response.get("commands", [])
        command_outputs = []
        steps.append("Processing terminal command.")
        for cmd in commands:
            command_text = cmd["command"]
            description = cmd["description"]
            steps.append(f"Executing: {command_text} - {description}")
            speak(f"Executing: {command_text} for {description}")
            print(f"Executing: {command_text} - {description}")
            output = execute_command(command_text)
            print(f"Output:\n{output}")
            command_outputs.append({"command": command_text, "output": output})
        return {"executed_commands": command_outputs}

    elif query_class == "debugging":
        suggestions = gemini_response.get("debugging_suggestions", {})
        steps.append("Processing debugging request.")
        speak("Processing debugging request. Providing suggestions.")
        print(f"Debugging Suggestions: {suggestions}")
        interactive_debugging(suggestions)

    elif query_class == "file_query":
        file_name = gemini_response.get("file_name", "")
        file_content = gemini_response.get("file_content", "")
        steps.append(f"Processing file query for {file_name}.")
        speak(f"Processing file query for {file_name}.")
        if file_name and not file_content:
            file_content = read_file(file_name)
        print(f"File Content ({file_name}):\n{file_content}")
        return {"file_name": file_name, "file_content": file_content}
    
    else:
        steps.append("Unrecognized query class.")
        speak("Unrecognized query class.")
        print("Unrecognized query class.")
        return {"error": "Unknown query classification."}
