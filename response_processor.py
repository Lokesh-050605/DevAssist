import os
import subprocess
import re
from interactive_debug import interactive_debugging
from utils import speak
from query_generator import classify_query
from query_gemini import query_gemini, response_parser

def process_response(classification_result, gemini_response):
    query_class = classification_result.get("class", "None")

    if query_class == "general_query":
        response_text = gemini_response.get("general_response", "No response available.")
        speak("Processing a general query. Speaking the response aloud.")
        print("Assistant:", response_text)
        speak(response_text)
        return {"response": response_text}

    elif query_class == "terminal_command":
        commands = gemini_response.get("commands", [])
        if not commands:
            speak("No valid commands received.")
            return {"error": "No commands provided."}
        
        command_outputs = []
        for cmd in commands:
            command_text = cmd["command"]
            description = cmd["description"]
            print(f"Executing: {command_text} - {description}")
            speak(f"Executing {command_text}. {description}")

            if command_text.startswith("python") and command_text.endswith((".py", ".com")):
                result = execute_python_script(command_text)
            else:
                result = execute_command(command_text)

            if result["success"]:
                print(f"Output:\n{result['output']}")
                speak("Command executed successfully. Output: " + result["output"])
                command_outputs.append({"command": command_text, "output": result["output"]})
            else:
                print(f"Error:\n{result['error']}")
                speak("An error occurred.")
                if "No such file or directory" in result["error"]:
                    debug_result = {"suggestion": f"File not found. Please check if '{command_text.split()[-1]}' exists in your directory."}
                    speak(debug_result["suggestion"])
                    print(debug_result["suggestion"])
                else:
                    speak("Starting debug assistant.")
                    debug_result = debug_command_error(result["error"], command_text)
                command_outputs.append({"command": command_text, "error": result["error"], "debug": debug_result})
                break
        return {"executed_commands": command_outputs}

    elif query_class == "debugging":
        suggestions = gemini_response.get("debugging_suggestions", {})
        speak("Processing debugging request. Providing suggestions.")
        print(f"Debugging Suggestions: {suggestions}")
        debug_result = interactive_debugging(suggestions)
        return {"debugging_suggestions": suggestions, "debug_result": debug_result}

    else:
        speak("Unrecognized query class.")
        print("Unrecognized query class.")
        return {"error": "Unknown query classification."}

def execute_python_script(command):
    try:
        script_path = command.split("python ")[1].strip()
        if not os.path.exists(script_path):
            return {"success": False, "error": f"python: can't open file '{script_path}': [Errno 2] No such file or directory", "command": command}

        prompts = extract_input_prompts(script_path)
        process = subprocess.Popen(command, shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        inputs = []
        if prompts:
            for prompt in prompts:
                speak(prompt)
                print(f"{prompt} ", end="", flush=True)
                user_input = input()
                inputs.append(user_input)
        
        input_string = "\n".join(inputs) + "\n" if inputs else ""
        stdout, stderr = process.communicate(input=input_string)
        
        if process.returncode == 0:
            return {"success": True, "output": stdout.strip()}
        else:
            return {"success": False, "error": stderr.strip(), "command": command}
    except Exception as e:
        return {"success": False, "error": f"Execution failed: {str(e)}", "command": command}

def execute_command(command):
    try:
        process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            return {"success": True, "output": stdout.strip()}
        else:
            return {"success": False, "error": stderr.strip(), "command": command}
    except Exception as e:
        return {"success": False, "error": f"Execution failed: {str(e)}", "command": command}

def extract_input_prompts(script_path):
    prompts = []
    try:
        with open(script_path, "r", encoding="utf-8") as file:
            content = file.read()
            matches = re.findall(r'input\s*\(\s*["\'](.*?)["\']\s*\)', content)
            prompts.extend(matches)
    except Exception as e:
        print(f"Error reading script: {e}")
    return prompts


def debug_command_error(error_text, command):
    debug_input = f"Debug this error while running '{command}':\n{error_text}\nProvide detailed debugging suggestions including error category, probable causes, step-by-step fix, a suggested code fix, and an auto-fix command (e.g., pip install <module> for ModuleNotFoundError)."
    classification = classify_query(debug_input)
    gemini_response = query_gemini(debug_input, classification)
    if gemini_response is None or "error" in gemini_response:
        speak("Failed to get debugging suggestions due to API issue.")
        print("API error or quota exceeded.")
        return {"error": "API unavailable", "retry_after": "4 seconds"}
    parsed_response = response_parser(gemini_response, classification)
    suggestions = parsed_response.get("debugging_suggestions", {})
    if not suggestions:
        speak("No debugging suggestions available.")
        print("No suggestions from Gemini.")
        return {"error": "No suggestions provided"}
    return interactive_debugging(suggestions)