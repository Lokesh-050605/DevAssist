import google.generativeai as genai
import json
from config import configure_api
from utils import load_user_config




def classify_query(user_input):
    """Classifies the given query into a predefined category and extracts required fields."""
    
    classification_prompt = f'''
    You are a query classifier. Categorize the given user query into one of the following classes:
    - "general_query": For general questions like "What is LLM?", "Hi", etc.
    - "terminal_command": For requests that require a terminal command, such as "list files in the current directory", "check Python version".
    - "debugging": When the query includes an error message and requires debugging.
    - "file_query": When the user queries about a specific file's content.
    
    Additionally, if the query requires extra context (like a filename for file queries), extract those fields under "requires".
    
    Return a JSON object strictly in this format:
    {{
        "class": "<classified_class>",
        "requires": {{ "<required_field>": "<value>" }}
    }}
    
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
    """Generates a query based on the classification result."""
    user_config = load_user_config()  # Load user configuration
    query_class = classification_result.get("class", "None")
    required = classification_result.get("requires", {})
    os_name = user_config.get("os", "Windows 10")
    
    if query_class == "general_query":
        return user_input  # Return the user input as a normal query

    elif query_class == "terminal_command":
        prompt = {
            "instruction": "Convert the following natural language instruction into a valid terminal command.",
            "os": os_name,
            "input": user_input,
            "expected_output": (
                "Return the most relevant and accurate terminal command(s) in JSON format. "
                "If multiple commands are required to complete the task, return them in an array. "
                "Each command should be provided with a short description explaining its purpose. "
                "Ensure high relevance and correctness of the commands."
            ),
            "response_format": {
                "commands": [
                    {"command": "", "description": ""}
                ]
            }
        }
        return json.dumps(prompt)


    elif query_class == "debugging":
        prompt = {
            "instruction": "Analyze the given error message and provide a debugging solution.",
            "os": os_name,
            "error_message": required.get("error_message", ""),
            "context": user_config,  # Include user system details for debugging context
            "expected_output": "Return a JSON containing debugging steps."
        }
        return json.dumps(prompt)
    
    elif query_class == "file_query":
        prompt = {
            "instruction": "Analyze the provided file content and respond accordingly.",
            "file_name": required.get("file_name", ""),
            "file_content": required.get("file_content", ""),
            "expected_output": "Return the relevant information from the file content in JSON format."
        }
        return json.dumps(prompt)
    
    return "Invalid query classification."
















######################################################################rough use functions######################################
def test_query_classifier():
    configure_api()
    
    #user_config = load_user_config()  # Load user configuration

    test_cases = [
        {"input": "What is machine learning?", "expected_class": "general_query"},
        {"input": "List files in the current directory", "expected_class": "terminal_command"}
        
    ]
    
    for test in test_cases:
        print(f"\nUser Input: {test['input']}")
        classification_result = classify_query(test['input'])
        print("Classification Result:", classification_result)
        
        generated_query = generate_query(test['input'], classification_result)
        print("Generated Query:", generated_query)
        
        # try:
        #     json_query = json.loads(generated_query)
        #     print("JSON Output:", json.dumps(json_query, indent=4))
        # except json.JSONDecodeError:
        #     print("Generated output is not a valid JSON.")

# Run the test
if __name__ == "__main__":
    test_query_classifier()
