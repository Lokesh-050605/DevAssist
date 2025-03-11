import google.generativeai as genai
import json
import subprocess
from config import configure_api
from utils import load_user_config
import os

def extract_file_content(file_name):
    """Reads the content of a file and returns it as a string."""  
    if file_name and os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    return "No valid file found."


def execute_command(command):
    """Executes a shell command and returns the output."""
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {str(e)}"

def classify_query(user_input):
    """Classifies the given query and determines necessary prerequisites."""
    
    classification_prompt = f'''
    You are an intelligent query classifier and debugging assistant. Categorize the given user query into one of the following classes:
    - "general_query": For general questions like "What is LLM?", "Hi", etc.
    - "terminal_command": For requests that require a terminal command, such as "list files in the current directory" or "check Python version".
    - "debugging": When the query includes an error message and requires debugging.
    - "file_query": When the user queries about a specific file's content.

    Additionally, extract necessary fields under "requires"(only it is must for debugging for example when the command is about push changes to git then git status is required to generate the commit message needed on execution but git push command is not needed in required) based on the query type:
    - `"question": "<question to ask the user>"` → If clarification is needed.
    - `"command": "<command to execute>"` → If a terminal command should be run.
    - `"error_analysis": "<steps to diagnose and fix the issue>"` → If debugging, analyze and suggest steps to resolve.
    - `"file_content": "<filename>"` → If the error is related to a file and its content is needed.
    - `"installed_packages": "<package_name>"` → If the error is related to missing dependencies.
    - `"system_info": "<system_detail>"` → If debugging requires OS, Python version, etc.
    - `"db_schema": "<table_name>"` → If the issue is related to a database query.
 ### **Examples**:
    - **command**: `"push changes to git"`
      ```json
      {{
          "class": "terminal_command",
          "requires": {{
                "command": "git status"
          }}
      }}
      ```
    ### **Debugging-Specific Handling**:
    If the query contains an error:
    1. Identify the root cause.
    2. Determine what additional information is needed to debug.
    3. Suggest commands or ask for missing inputs.

    ### **Examples**:
    - **Python Import Error**: `"ModuleNotFoundError: No module named 'requests'"`
      ```json
      {{
          "class": "debugging",
          "requires": {{
              "error_message": "The 'requests' module is not installed.",
              "command": "pip show requests"
          }}
      }}
      ```
    - **Syntax Error in File**: `"SyntaxError: unexpected EOF while parsing in script.py"`
      ```json
      {{
          "class": "debugging",
          "requires": {{
              "error_analysis": "The script might be incomplete.",
              "file_content": "script.py"
          }}
      }}
      ```
    - **Database Error**: `"ERROR: relation 'users' does not exist"`
      ```json
      {{
          "class": "debugging",
          "requires": {{
              "error_analysis": "The 'users' table might be missing in the database.",
              "db_schema": "users"
          }}
      }}
      ```
    - **Git Error**: `"fatal: not a git repository"`
      ```json
      {{
          "class": "debugging",
          "requires": {{
              "error_analysis": "You're not in a Git repository. Running 'git status' to check.",
              "command": "git status"
          }}
      }}
      ```

    ### **Expected JSON format**:
    ```json
    {{
        "class": "<classified_class>",
        "requires": {{
            "<required_field>": "<value>"
        }}
    }}
    ```

    Ensure:
    - The response is always valid JSON.
    - Only relevant fields are included in "requires".
    - If no extra input is required, "requires" should be an empty object.

    User Query: "{user_input}"
    '''

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(classification_prompt)

    try:
        clean_response = response.text.strip('```json\n').strip('```')  # Handle incorrect formatting
        return json.loads(clean_response)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from Gemini."}




def generate_query(user_input, classification_result):
    """Generates a structured query based on the classification result, either by asking the user for missing input or executing a command."""

    user_config = load_user_config() 
    query_class = classification_result.get("class", "None")
    required = classification_result.get("requires", {})
    os_name = user_config.get("os", "Windows 10")

    # Handle missing input by asking the user
    if "question" in required:
        required_value = input(f"{required['question']} ")  # Ask user
        required["user_response"] = required_value 

    # Execute required command and capture output
    if "command" in required:
        try:
            command_output = subprocess.check_output(required["command"], shell=True, text=True).strip()
            required["command_output"] = command_output  # Store command output
        except subprocess.CalledProcessError as e:
            required["command_output"] = f"Error executing command: {str(e)}"
    # Extract file content if 'file_name' exists
    if "file_content" in required:
        required["file_name"] = required["file_name"]
        required["file_content"] = extract_file_content(required["file_content"])

    # Generate prompt based on query classification
    if query_class == "general_query":
       return user_input + " Provide a **concise** answer (within 2-3 sentences) as this will be read aloud to a visually impaired developer."

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
        if not user_input:
            return json.dumps({"error": "No error message provided for debugging."}, indent=4)

        prompt = {
            "instruction": (
                "You are an AI-powered debugging assistant helping a **blind developer** using a terminal. "
                "Analyze the given error message, classify it (Syntax Error, Import Error, Runtime Error, etc.), "
                "and provide a structured, step-by-step debugging guide."
            ),
            "os": os_name,
            "error_message": user_input,
            "error": error_message,
            "context": user_config, 
            "debugging_type": (
                "Detect and classify the error as one of the following: Syntax Error, Import Error, "
                "Runtime Error, Logical Error, Compilation Error, Dependency Error, or Other."
            ),
            "requires": required,
            "response_format": {
                "error_category": "<Identified Error Type>",
                "probable_causes": ["<Possible cause 1>", "<Possible cause 2>"],
                "step_by_step_fix": [
                    "<Ask the user if they want to check something>",
                    "<If yes, provide the command>",
                    "<Ask user if they want to execute the fix>"
                ],
                "suggested_fix": "<Best solution>",
                "auto_fix_command": "<Command to execute the fix>",
                "alternative_solutions": ["<Alternative approach 1>", "<Alternative approach 2>"],
                "preventive_measures": ["<Best practices to avoid similar issues>"]
            }
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
