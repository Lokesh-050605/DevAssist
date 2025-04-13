# query_generator.py
import google.generativeai as genai
import json
import subprocess
from config import configure_api
from utils import load_user_config
import os
import re

def extract_file_content(file_name):
    if file_name and os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    return "No valid file found."

def execute_command(command):
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {str(e)}"

def classify_query(user_input):
    """Classifies the given query and determines necessary prerequisites."""
    user_config = load_user_config()
    os_name = user_config.get("os", "Windows 10")
    
    classification_prompt = f'''
    You are a query classifier running on {os_name}. Classify this query:
    - "general_query": General questions (e.g., "What is LLM?").
    - "terminal_command": Terminal commands (e.g., "list files in the current directory").
    - "debugging": Error messages (e.g., "ModuleNotFoundError").
    - "file_query": File operations (e.g., "open test.py", "insert print hi at line 2 in test.py", "find function in test.py", "add code to test.py").

    OS: {os_name}. Use {os_name}-compatible commands only (e.g., "dir" not "ls").
    "requires" should include only safe information-gathering prerequisites (e.g., "git status", "pip show <pkg>", not install/modify commands).

    
    - "open <file>" → {{"action": "open", "filename": "<file>"}}
    - "insert <content> at line <num> in <file>" → {{"action": "insert", "content": "<content>", "line": <num>, "filename": "<file>"}}
    - "find <target> in <file>" → {{"action": "find", "target": "<target>", "filename": "<file>"}}
    - "add/append <content> to <file>" → {{"action": "append", "content": "<content>", "filename": "<file>"}}

    Return valid JSON: {{"class": "<class>", "requires": {{<fields>}}}}.
    If error, return {{"class": "error", "requires": {{"message": "<reason>"}}}}.
    Examples:
    - "list files in the current directory" → {{"class": "terminal_command", "requires": {{}}}}
    - "push changes to git" → {{"class": "terminal_command", "requires": {{"command": "git status"}}}}
    - - "ModuleNotFoundError: No module named 'requests'" → {{"class": "debugging", "requires": {{"check_module": "requests"}}}}
    - "open test.py" → {{"class": "file_query", "requires": {{"action": "open", "filename": "test.py"}}}}
    - "insert print hi at line 2 in test.py" → {{"class": "file_query", "requires": {{"action": "insert", "content": "print hi", "line": 2, "filename": "test.py"}}}}
    - "find function that adds numbers in test.py" → {{"class": "file_query", "requires": {{"action": "find", "target": "function that adds numbers", "filename": "test.py"}}}}
    - "run" → {{"class": "terminal_command"}}
    
    Query: "{user_input}"
    Return strict JSON, no extra text.
    '''


    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(classification_prompt)
        if response and hasattr(response, 'text') and response.text:
            raw_response = response.text.strip()
            print(f"Raw Gemini response: '{raw_response}'")  # Debug log
            
            # Extract JSON from markdown if present
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                clean_response = json_match.group(0)
            else:
                clean_response = raw_response
            
            if not clean_response:
                return {"class": "error", "requires": {"message": "Gemini returned empty response"}}
            
            return json.loads(clean_response)
        else:
            return {"class": "error", "requires": {"message": "No valid response from Gemini"}}
    except json.JSONDecodeError as e:
        print(f"Gemini JSON error: {e}")
        return {"class": "error", "requires": {"message": f"Invalid JSON from Gemini: {str(e)}"}}
    except Exception as e:
        print(f"Gemini error: {e}")
        return {"class": "error", "requires": {"message": f"Gemini failed: {str(e)}"}}

def generate_query(user_input, classification_result):
    user_config = load_user_config()
    query_class = classification_result.get("class", "None")
    required = classification_result.get("requires", {})
    os_name = user_config.get("os", "Windows 10")

    if "question" in required:
        required_value = input(f"{required['question']} ")
        required["user_response"] = required_value 

    if "command" in required:
        try:
            command_output = subprocess.check_output(required["command"], shell=True, text=True).strip()
            required["command_output"] = command_output
        except subprocess.CalledProcessError as e:
            required["command_output"] = f"Error executing command: {str(e)}"
    
    if "file_content" in required:
        required["file_name"] = required["file_content"]
        required["file_content"] = extract_file_content(required["file_content"])
    
    if "check_module" in required:
        module = required["check_module"]
        try:
            output = subprocess.check_output(f"pip show {module}", shell=True, text=True).strip()
            required["module_info"] = output or f"Module '{module}' not found"
        except subprocess.CalledProcessError as e:
            required["module_info"] = f"Module '{module}' not found"


    if query_class == "general_query":
        return user_input + " Provide a concise answer (2-3 sentences) for a visually impaired developer."
    elif query_class == "terminal_command":
        prompt = {
            "instruction": f"Convert to a valid {os_name} terminal command.",
            "os": os_name,
            "input": user_input,
            "requires": required,
            "response_format": {"commands": [{"command": "<command>", "description": "<explanation>"}]}
        }
        return json.dumps(prompt, indent=4)
    elif query_class == "debugging":
        return json.dumps({"instruction": "Debug this", "input": user_input, "requires": required})
    elif query_class == "file_query":
        action = required.get("action")
        if action == "open":
            return json.dumps({"instruction": f"Open file {required['filename']} in Neovim", "requires": required})
        elif action == "insert":
            return json.dumps({"instruction": f"Insert '{required['content']}' at line {required['line']} in {required['filename']}", "requires": required})
        elif action == "find":
            return json.dumps({"instruction": f"Find '{required['target']}' in {required['filename']} and return line number", "requires": required})
        elif action == "append":
            return json.dumps({"instruction": f"Append '{required['content']}' to {required['filename']}", "requires": required})
        action = required.get("action")
        if action == "open":
            return json.dumps({"instruction": f"Open file {required['filename']} in Neovim", "requires": required})
        elif action == "insert":
            return json.dumps({"instruction": f"Insert '{required['content']}' at line {required['line']} in {required['filename']}", "requires": required})
        elif action == "find":
            return json.dumps({"instruction": f"Find '{required['target']}' in {required['filename']} and return line number", "requires": required})
        elif action == "append":
            return json.dumps({"instruction": f"Append '{required['content']}' to {required['filename']}", "requires": required})
    return json.dumps({"error": "Invalid query classification."}, indent=4)