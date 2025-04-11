import google.generativeai as genai
import json
import time
from query_generator import classify_query, generate_query

last_request_time = 0
min_interval = 4  # 4 sec delay for 15 RPM (Flash)

def query_gemini(user_input, classification_result):
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < min_interval:
        delay = min_interval - time_since_last
        print(f"Rate limit: Waiting {delay:.2f} seconds before next API call...")
        time.sleep(delay)
    
    if "error" in classification_result:
        return {"error": "Failed to classify query."}
    
    formatted_prompt = generate_query(user_input, classification_result)
    
    if formatted_prompt.startswith("{\"error\""):
        return json.loads(formatted_prompt)

    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        if classification_result["class"] == "terminal_command":
            formatted_prompt += "\nReturn response in strict JSON format: {\"commands\": [...]}. If multiple commands, provide in order."
        elif classification_result["class"] == "debugging":
            formatted_prompt += "\nReturn response in strict JSON format: {\"error_category\": \"<category>\", \"probable_causes\": [], \"step_by_step_fix\": [], \"suggested_fix\": \"\", \"auto_fix_command\": \"\"}"
        
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

        return {"error": f"Unknown query classification: {query_class}"}

    except (json.JSONDecodeError, AttributeError) as e:
        return {"error": f"Parsing error: {str(e)}"}