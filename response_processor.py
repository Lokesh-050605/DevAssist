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
    - Reads aloud general queries.
    - Executes terminal commands and displays output.
    - Provides debugging solutions.
    - Handles file queries.
    """

    query_class = classification_result.get("class", "None")

    if query_class == "general_query":
        # Read aloud the response
        print(gemini_response)
        response_text = gemini_response.get("general_response", "No response available.")
        print("Assistant:", response_text)
        speak(response_text)
        return response_text

    elif query_class == "terminal_command":
        commands = gemini_response.get("commands", [])
        command_outputs = []

        for cmd in commands:
            command_text = cmd["command"]
            description = cmd["description"]
            print(f"\nExecuting: {command_text}\n {description}")
            output = execute_command(command_text)
            print(f"Output:\n{output}")
            command_outputs.append({"command": command_text, "output": output})

        return {"executed_commands": command_outputs}

    elif query_class == "debugging":
        suggestions = gemini_response.get("debugging_suggestions", {})
        print(10*"#")
        print(f"Debugging Suggestions: {suggestions}")
        interactive_debugging(suggestions)

    elif query_class == "file_query":
        file_name = gemini_response.get("file_name", "")
        file_content = gemini_response.get("file_content", "")

        if file_name and not file_content:
            file_content = read_file(file_name)

        print(f"File Content ({file_name}):\n{file_content}")
        return {"file_name": file_name, "file_content": file_content}

    else:
        print("Unrecognized query class.")
        return {"error": "Unknown query classification."}

# Example usage
from query_generator import classify_query
from query_gemini import query_gemini,response_parser


user_input ='''push changes to git'''

# user_input ='''ModuleNotFoundError: No module named 'requests' '''
classification_result = classify_query(user_input)
gemini_response = query_gemini(user_input,classification_result)

parsed_response =response_parser(gemini_response, classification_result)

process_response(classification_result, parsed_response)