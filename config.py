import os
import google.generativeai as genai

def configure_api():
    #gemini_api_key = os.getenv("GEMINI_API_KEY","AIzaSyDl0frUYzjFR16T_PPk2vBtLyCmyhfn9sg")
    gemini_api_key = "AIzaSyDl0frUYzjFR16T_PPk2vBtLyCmyhfn9sg"
    if not gemini_api_key:
        raise ValueError("ERROR: GEMINI_API_KEY not found. Please set it as an environment variable.")
    try:
        genai.configure(api_key=gemini_api_key)
        print("Google Generative AI API configured successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to configure Generative AI API: {e}")

# No close method needed, Gemini handles internally
def close_api_connection():
    print("Gemini API connection cleanup not required.")