import google.generativeai as genai
import json
from query_generator import classify_query, generate_query


def query_gemini(user_input,classification_result):
    """Classifies the query, generates a structured prompt, and fetches Gemini's response."""
    
    if "error" in classification_result:
        return {"error": "Failed to classify query."}
    
    # Step 2: Generate the structured query for Gemini
    formatted_prompt = generate_query(user_input, classification_result)
    
    if formatted_prompt.startswith("{\"error\""):
        return json.loads(formatted_prompt)  # Return error response directly

    # Step 3: Send request to Gemini API
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(formatted_prompt)

    return response

def response_parser(response, classification):
    """Parses the response from Gemini based on the classification result."""

    print(f"Response: {response}")
    print(f"Classification: {classification}")

    try:
        # Extract text response
        response_text = response.text

        # Process classification type
        query_class = classification.get("class", "None")

        if query_class == "general_query":
            return {"general_response": response_text}

        elif query_class == "terminal_command":
            try:
                response_text = response_text.strip('```json\n').strip('```')  # Handle incorrect formatting
                parsed_response = json.loads(response_text)
                if isinstance(parsed_response, dict) and "commands" in parsed_response:
                    return {"commands": parsed_response["commands"]}
            except json.JSONDecodeError:
                return {"error": "Invalid JSON format in terminal command response."}

        elif query_class == "debugging":
            return {"debugging_suggestions": response_text}

        elif query_class == "file_query":
            try:
                parsed_response = json.loads(response_text)
                return {
                    "file_name": parsed_response.get("file_name", ""),
                    "file_content": parsed_response.get("file_content", "File content not provided.")
                }
            except json.JSONDecodeError:
                return {"error": "Invalid JSON format in file query response."}

        else:
            return {"error": f"Unknown query classification: {query_class}"}

    except (IndexError, AttributeError) as e:
        return {"error": f"Parsing error: {str(e)}"}

# # Example usage
# user_input = "push changes to git"
# result = query_gemini(user_input)
# print(json.dumps(result, indent=4))
