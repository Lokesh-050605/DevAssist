#commands processor.py
import json
from response_processor import process_response
from utils import speak
from query_generator import classify_query
from query_gemini import query_gemini, response_parser

def process_command(user_input):
    """Processes user commands and provides appropriate responses."""
    # Classify the query
    classification_result = classify_query(user_input)
    print("Classification Result: \n", json.dumps(classification_result, indent=4))
    
    # Announce the classification to the user
    speak("Query classified.")
    
    # Query Gemini for a response based on the classification
    gemini_response = query_gemini(user_input, classification_result)
    print("Gemini Response: \n", gemini_response)
    
    # Parse the response from Gemini
    parsed_response = response_parser(gemini_response, classification_result)
    print("Parsed Response: \n", json.dumps(parsed_response, indent=4))
    
    # Announce that the command is being processed
    speak("Processing command.")
    
    # Process the final response
    process_response(classification_result, parsed_response)

