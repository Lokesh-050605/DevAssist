import re
import google.generativeai as genai
import json
import time
from query_generator import generate_query

last_request_time = 0
min_interval = 4  # 4 sec delay for 15 RPM (Flash)

def query_gemini(user_input, classification_result,filename=None):
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < min_interval:
        delay = min_interval - time_since_last
        print(f"Rate limit: Waiting {delay:.2f} seconds before next API call...")
        time.sleep(delay)

    if "error" in classification_result:
        return {"error": "Failed to classify query."}
    
    formatted_prompt = generate_query(user_input, classification_result,filename)
    
    if formatted_prompt.startswith("{\"error\""):
        return json.loads(formatted_prompt)

    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        if classification_result["class"] == "terminal_command":
            formatted_prompt += (
                "\nReturn response in strict JSON format: "
                "{\"commands\": [{\"command\": \"<cmd>\", \"description\": \"<desc>\"}]}. "
                "If the task requires multiple sequential commands (e.g., git push), "
                "provide them in the correct order as an array."
                "give commands with -y flag if needed. "
                "use the information gathered by required to generate the command. "
                "example for commit commmand give commit message based on the changes made gathered by git status in required"
            )

        elif classification_result["class"] == "debugging":
            formatted_prompt += (
                "\nReturn the response in this exact JSON format:\n"
                "{\n"
                "  \"error_category\": \"<category>\",\n"
                "  \"probable_causes\": [\"cause1\", \"cause2\"],\n"
                "  \"step_by_step_fix\": [\"step1\", \"step2\"],\n"
                "  \"suggested_fix\": \"<explanation>\",\n"
                "  \"auto_fix_command\": \"<only if it is VALID and RELEVANT>\"\n"
                "}\n"
                "Include an auto_fix_command ONLY IF it is guaranteed to be effective and safe to run. "
                "If unsure or if it's risky, leave the field empty. "
                "Do not return placeholder or made-up commands."
            )
        if classification_result["class"]=="file_query":
            required = classification_result.get("requires", {})
            if required["action"]=="open":
                return {"action": "open", "filename": required["filename"]}
            elif required["action"]=="insert":
                formatted_prompt += f"""
                        Instructions:

                        - Identify where to insert the code specified in the user command (e.g., print("hiii")).
                        - If the user specifies 'above <code>' (e.g., 'above a1=10'), analyze the file_content to find the line number of '<code>' and use the line before it.
                        - If a specific line number is provided, use that.
                        - Generate the content to insert based on the file context (e.g., for a Python file, use Python syntax like print("hiii") for a print statement).
                        - Return the response in this exact JSON format: 
                            {{
                                "action": "<action>", 
                                "content": "<content>", 
                                "line_no": <line_no>
                            }} 
                    """
            elif required["action"]=="find":
                formatted_prompt += f"""
                        Instructions:

                        - Identify a function or statement matching the functionality described in the user command (e.g., 'function that find sum' or 'where we get input for num').
                        - Analyze the file_content to find the function or statement.
                        - Return the response in this exact JSON format: 
                            {{
                                "action": "find",
                                "function_name": "<function_name_or_statement>",
                                "line_no": <line_no>
                            }}
                        - If no match is found, return empty function_name and line_no 1.  
                    """
                
            elif required["action"]=="append":
                formatted_prompt += f"""
                    Instructions:
                
                        -Generate the content to append based on the user command and file context (e.g., for a Python file, use Python syntax like print("hiii") for a print statement).
                        -The content will be appended to the end of the file.
                        -Return the response in this exact JSON format: 
                            {{
                                "action": "append", 
                                "content": "<content>",
                            }}
                        -Set line_no to the line number where the content will be appended (the new last line number).
                    """
            elif required["action"] == "replace":
                formatted_prompt += f"""
                    Instructions:

                    - From the user command, extract the word or phrase to **find** and the word or phrase to **replace it with**.
                    - Return the response in this exact JSON format:
                        {{
                            "action": "replace",
                            "old_word": "<old_word>",
                            "new_word": "<new_word>"
                        }}
                    - If either word is unclear or missing, return an empty string for that field.
                    - Only extract exact strings; no explanations.
                """
        # print(f"Generated Prompt : \n{formatted_prompt}")
        response = model.generate_content(formatted_prompt)
        last_request_time = time.time()
        return response

    except Exception as e:
        print(f"Gemini API error: {e}")
        return None

def response_parser(response, classification):
    try:
        if not hasattr(response, 'text') or not response.text:
            return {"error": "No valid response from Gemini"}
        response_text = response.text.strip('```json\n').strip('```')

        query_class = classification.get("class", "None")

        if query_class == "general_query":
            return {"general_response": response_text}

        elif query_class == "terminal_command":
            return {"commands": json.loads(response_text)["commands"]}

        elif query_class == "debugging":
            try:
                parsed_response = json.loads(response_text)
                suggestions = {
                    "error_category": parsed_response.get("error_category", "Unknown"),
                    "probable_causes": parsed_response.get("probable_causes", []),
                    "step_by_step_fix": parsed_response.get("step_by_step_fix", []),
                    "suggested_fix": parsed_response.get("suggested_fix", ""),
                    "auto_fix_command": parsed_response.get("auto_fix_command", "")
                }
                if not any(suggestions.values()):
                    return {"error": "Incomplete debugging response", "raw_text": response_text}
                return {"debugging_suggestions": suggestions}
            except json.JSONDecodeError:
                return {"error": "Invalid JSON format in debugging response", "raw_text": response_text}
        
        elif query_class == "file_query":
                if(classification["requires"]["action"]=="open"):
                    return response
                elif classification["requires"]["action"]=="insert":
                    formatted_response = json.loads(response_text)
                    action = formatted_response.get("action")
                    content = formatted_response.get("content")
                    line_no = formatted_response.get("line_no")

                    if not action or not content or line_no is None:
                        return {"error": "Incomplete response from Gemini", "raw_text": response_text}
                    
                    return {
                        "action": action,
                        "content": content,
                        "line_no": line_no
                    }
                elif classification["requires"]["action"]=="find":
                    formatted_response = json.loads(response_text)
                    action = formatted_response.get("action")
                    function_name = formatted_response.get("function_name")
                    line_no = formatted_response.get("line_no")

                    if not action or not function_name or line_no is None:
                        return {"error": "Incomplete response from Gemini", "raw_text": response_text}
                    
                    return {
                        "action": action,
                        "function_name": function_name,
                        "line_no": line_no
                    }
                elif classification["requires"]["action"]=="append":    
                    cleaned_text = re.sub(r',\s*([\]}])', r'\1', response_text)
                    formatted_response = json.loads(cleaned_text)
                    print(f"formatted_response: {formatted_response}")
                    action = formatted_response.get("action")
                    content = formatted_response.get("content")

                    if not action or not content:
                        return {"error": "Incomplete response from Gemini", "raw_text": response_text}
                    
                    return {
                        "action": action,
                        "content": content,
                    }
                
                elif classification["requires"]["action"] == "replace":
                    formatted_response = json.loads(response_text)
                    action = formatted_response.get("action")
                    old_word = formatted_response.get("old_word")
                    new_word = formatted_response.get("new_word")

                    if not action or old_word is None or new_word is None:
                        return {"error": "Incomplete replace response", "raw_text": response_text}

                    return {
                        "action": action,
                        "old_word": old_word,
                        "new_word": new_word
                    }


        return {"error": f"Unknown query classification: {query_class}"}

    except (json.JSONDecodeError, AttributeError) as e:
        return {"error": f"Parsing error: {str(e)}"}