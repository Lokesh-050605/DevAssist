import json
from response_processor import process_response
from utils import speak
from query_generator import classify_query
from query_gemini import query_gemini, response_parser

def process_command(user_input):
    """Processes user commands and provides appropriate responses."""
    
    classification_result = classify_query(user_input)
    print("Classification Result:", classification_result)
    speak(f"{classification_result['class']} type query.")
    
    gemini_response = query_gemini(user_input, classification_result)
    parsed_response = response_parser(gemini_response, classification_result)
    
    speak("Processing command...")
    
    response = process_response(classification_result, parsed_response)

    # Instead of recursive call, check if an error occurred
    if isinstance(response, dict) and "error" in response:
        print("Error:", response["error"])
        speak("An error occurred while processing your command.")
    
    return response
