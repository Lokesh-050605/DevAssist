import google.generativeai as genai
import json
from query_generator import classify_query, generate_query


def query_gemini(user_input):
    """Classifies the query, generates a structured prompt, and fetches Gemini's response."""
    
    # Step 1: Classify the query
    classification_result = classify_query(user_input)
    
    if "error" in classification_result:
        return {"error": "Failed to classify query."}
    
    # Step 2: Generate the structured query for Gemini
    formatted_prompt = generate_query(user_input, classification_result)
    
    if formatted_prompt.startswith("{\"error\""):
        return json.loads(formatted_prompt)  # Return error response directly

    # Step 3: Send request to Gemini API
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(formatted_prompt)
    
    try:
        # Step 4: Extract JSON from response
        clean_response = response.text.strip("```json\n").strip("```")
        parsed_response = json.loads(clean_response)
        
        # Ensure the response follows the expected format
        if "commands" in parsed_response and isinstance(parsed_response["commands"], list):
            return parsed_response  # Return parsed command list

        return {"error": "Invalid response format from Gemini."}
    
    except (json.JSONDecodeError, AttributeError):
        return {"error": "Failed to parse Gemini's response."}


# # Example usage
# user_input = "push changes to git"
# result = query_gemini(user_input)
# print(json.dumps(result, indent=4))
