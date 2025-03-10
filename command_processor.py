from response_processor import process_response
from utils import speak
from query_generator import classify_query
from query_gemini import query_gemini,response_parser

def process_command(user_input):
    """Processes user commands and provides appropriate responses."""
    classification_result = classify_query(user_input)
    print("Classification Result:", classification_result)
    speak("Query classified.")
    gemini_response = query_gemini(user_input,classification_result)
    print("Gemini Response:", gemini_response)
    parsed_response =response_parser(gemini_response, classification_result)
    print("Parsed Response:", parsed_response)
    speak("Processing command.")
    process_response(classification_result, parsed_response)