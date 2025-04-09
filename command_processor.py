#command_processor.py
import json
from response_processor import process_response
from utils import speak
from query_generator import classify_query
from query_gemini import query_gemini, response_parser

def process_command(user_input):
    """Processes user commands and provides appropriate responses."""
    
    classification_result = classify_query(user_input)
    if not classification_result or "class" not in classification_result:
        print("Error: Classification failed.")
        speak("Sorry, I couldn’t classify your command.")
        return "Error: Classification failed"
    
    print("Classification Result:", classification_result)
    if classification_result["class"] == "error":
        print("Error from classifier:", classification_result["requires"]["message"])
        speak("Sorry, there was an issue processing your command.")
        return "Error: " + classification_result["requires"]["message"]
    
    speak(f"{classification_result['class']} type query.")
    
    gemini_response = query_gemini(user_input, classification_result)
    if gemini_response is None:
        print("Error: No response from Gemini.")
        speak("Sorry, I couldn’t get a response from the assistant.")
        return "Error: No Gemini response"
    
    parsed_response = response_parser(gemini_response, classification_result)
    if parsed_response is None:
        print("Error: Failed to parse Gemini response.")
        speak("An error occurred while processing your command.")
        return "Error: Parsing failed"
    
    speak("Processing command...")
    response = process_response(classification_result, parsed_response)

    if isinstance(response, dict) and "error" in response:
        print("Error:", response["error"])
        speak("An error occurred while processing your command.")
        return response["error"]
    
    return response