import google.generativeai as genai
import json
from config import configure_api
from utils import load_user_config


def classify_query(user_input):
    """Classifies the given query into a predefined category and extracts required fields."""
    
    classification_prompt = f'''
    You are a query classifier. Categorize the given user query into one of the following classes:
    - "general_query": For general questions like "What is LLM?", "Hi", etc.
    - "terminal_command": For requests that require a terminal command, such as "list files in the current directory" or "check Python version".
    - "debugging": When the query includes an error message and requires debugging.
    - "file_query": When the user queries about a specific file's content.

    Additionally, if the query requires extra context (e.g., a filename for file queries), extract the necessary fields under "requires".

    If additional input is required, include it in `"requires"` using:
    - `"question": "<question to ask the user>"` → When clarification from the user is needed.
    - `"command": "<command to execute>"` → When a terminal command should be run to gather required information.

    ### **Examples**:
    - For `"git push"`, include `"command": "git status"` to get changes before pushing.
    - For `"clone a repository"`, include `"question": "Provide the repository link to clone."`
    - For `"run a C program"`, include `"question": "Which C file do you want to compile and run?"`

    ### **Expected JSON format**:
    ```json
    {{
        "class": "<classified_class>",
        "requires": {{
            "<required_field>": "<value>"
        }}
    }}

    Ensure that:
    - Only relevant fields are included in "requires".
    - If no extra input is required, "requires" should be an empty object.
    - The response is always valid JSON.

    User Query: "{user_input}"
    '''

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(classification_prompt)

    try:
        clean_response = response.text.strip('```json\n').strip('```')  # Handle incorrect formatting
        return json.loads(clean_response)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Gemini."}


import subprocess

def generate_query(user_input, classification_result):
    """Generates a structured query based on the classification result, either by asking the user for missing input or executing a command."""

    user_config = load_user_config()  # Load user configuration
    query_class = classification_result.get("class", "None")
    required = classification_result.get("requires", {})
    os_name = user_config.get("os", "Windows 10")

    # Handle missing input by asking the user
    if "question" in required:
        required_value = input(f"{required['question']} ")  # Ask user
        required["user_response"] = required_value  # Store user response

    # Execute required command and capture output
    if "command" in required:
        try:
            command_output = subprocess.check_output(required["command"], shell=True, text=True).strip()
            required["command_output"] = command_output  # Store command output
        except subprocess.CalledProcessError as e:
            required["command_output"] = f"Error executing command: {str(e)}"

    # Generate prompt based on query classification
    if query_class == "general_query":
        return user_input  # Return user input as normal query

    elif query_class == "terminal_command":
        prompt = {
            "instruction": (
                "Convert the given natural language instruction into a valid terminal command. "
                "Analyze the 'requires' field for additional context (e.g., specific file names, "
                "git status results, or other necessary inputs) and incorporate them correctly "
                "generate the commit message. Ensure to include all relevant information"
                "into the command."
            ),
            "os": os_name,
            "input": user_input,
            "requires": required,  # Attach user input or command output
            "expected_output": (
                "Return the most relevant and accurate terminal command(s) in strict JSON format. "
                "If multiple commands are required, return them as an array in execution order. "
                "Ensure commands are syntactically correct and optimized for the given OS. "
                "Each command should have a 'description' explaining its purpose."
            ),
            "response_format": {
                "commands": [
                    {"command": "<actual_command_here>", "description": "<explanation_here>"}
                ]
            }
        }

        return json.dumps(prompt, indent=4)

    elif query_class == "debugging":
        error_message = required.get("error_message", "")
        if not error_message:
            return json.dumps({"error": "No error message provided for debugging."}, indent=4)

        prompt = {
            "instruction": "Analyze the given error message and provide a debugging solution.",
            "os": os_name,
            "error_message": error_message,
            "requires": required,  # Attach user input or command output
            "context": user_config,
            "expected_output": "Return a JSON containing debugging steps and possible solutions."
        }
        return json.dumps(prompt, indent=4)

    elif query_class == "file_query":
        file_name = required.get("file_name", "")
        file_content = required.get("file_content", "")

        if not file_name:
            return json.dumps({"error": "File name is required for file queries."}, indent=4)

        prompt = {
            "instruction": "Analyze the provided file content and respond accordingly.",
            "file_name": file_name,
            "file_content": file_content,
            "requires": required,  # Attach user input or command output
            "expected_output": "Return relevant information from the file content in JSON format."
        }
        return json.dumps(prompt, indent=4)

    return json.dumps({"error": "Invalid query classification."}, indent=4)




##############################################
