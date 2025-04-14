import os
import subprocess
from interactive_debug import interactive_debugging
from nvim_handler import NvimHandler
from utils import speak
from query_generator import classify_query
from query_gemini import query_gemini, response_parser
from run_terminal_command import execute_command

nvim_handler = NvimHandler()

def process_response(classification_result, gemini_response,file_name):
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

            
            result = execute_command(command_text)
            print(f"Command result: {result}")
            if result["success"]:
                speak("Command executed successfully.")
                command_outputs.append({"command": command_text, "output": result["output"]})
            else:
                print(f"Error:\n{result['error']}")
                speak("An error occurred.")
                if "No such file or directory" in result["error"]:
                    debug_result = {"suggestion": f"File not found. Please check if '{command_text.split()[-1]}' exists in your directory."}
                else:
                    speak("Starting debug assistant.")
                    debug_result = debug_command_error(result["error"], command_text)
                command_outputs.append({"command": command_text, "error": result["error"], "debug": debug_result})
                break
        return {"executed_commands": command_outputs}

    elif query_class == "file_query":
        requires = classification_result.get("requires", {})
        action = requires.get("action")
    
        if action == "open":
            filename = requires.get("filename")
            if not filename:
                speak("No filename provided.")
                return {"error": "No filename specified"}
            print(f"nvim_handler in open: {nvim_handler}")
            return nvim_handler.open_file(filename)

        elif action == "insert":
            content = gemini_response.get("content")
            line = gemini_response.get("line_no")
            if not file_name:
                speak("No filename provided.")
                return {"error": "No filename specified"}
            if not content or not line:
                speak("Missing content or line number.")
                return {"error": "Missing content or line number"}
            return nvim_handler.insert_line(file_name, content, line)

        elif action == "find":
            function_name = gemini_response.get("function_name")
            line_no = gemini_response.get("line_no")
            if not file_name:
                speak("No filename provided.")
                return {"error": "No filename specified"}
            if not function_name or not line_no:
                speak("Missing function name or line number.")
                return {"error": "Missing function name or line number"}
            print(f"nvim_handler in find: {nvim_handler}")
            return nvim_handler.find_function(file_name, function_name, line_no)

        elif action == "append":
            print(f"gemini_response: {gemini_response}")
            content = gemini_response.get("content")
            if not content:
                speak("No content provided to append.")
                return {"error": "No content specified"}
            return nvim_handler.append_to_file(file_name, content)
        
        elif action == "replace":
            old_word = gemini_response.get("old_word")
            new_word = gemini_response.get("new_word")
            if not all([file_name, old_word, new_word]):
                speak("Missing filename or replacement words.")
                return {"error": "Missing replace arguments"}
            return nvim_handler.replace_word(file_name, old_word, new_word,case_sensitive=False)


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

# def execute_python_script(command):
#     try:
#         script_path = command.split("python ")[1].strip()
#         if not os.path.exists(script_path):
#             return {"success": False, "error": f"python: can't open file '{script_path}': [Errno 2] No such file or directory", "command": command}
#         process = subprocess.Popen(command, shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         stdout, stderr = process.communicate(timeout=30)
#         if process.returncode == 0:
#             return {"success": True, "output": stdout.strip()}
#         else:
#             return {"success": False, "error": stderr.strip(), "command": command}
#     except subprocess.TimeoutExpired:
#         process.kill()
#         return {"success": False, "error": f"Command timed out after 30 seconds", "command": command}
#     except Exception as e:
#         return {"success": False, "error": f"Execution failed: {str(e)}", "command": command}

# def execute_command(command):
#     try:
#         if "pip uninstall" in command:
#             command += " -y"
#         result = subprocess.run(command, shell=True, text=True, capture_output=True, timeout=30)
#         if result.returncode == 0:
#             return {"success": True, "output": result.stdout.strip()}
#         else:
#             return {"success": False, "error": result.stderr.strip(), "command": command}
#     except subprocess.TimeoutExpired:
#         return {"success": False, "error": f"Command timed out after 30 seconds", "command": command}
#     except Exception as e:
#         return {"success": False, "error": f"Execution failed: {str(e)}", "command": command}

def extract_file_content(file_name):
    if file_name and os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    return "No valid file found."

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