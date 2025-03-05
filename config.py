import os
import google.generativeai as genai

#set GEMINI_API_KEY=AIzaSyB-ibPnz6E9rW-I4jfME879TCulX-yt5Dg
#echo %GEMINI_API_KEY%
def configure_api():
    """
    Configures the Google Generative AI API with an API key from environment variables.
    Raises an error if the key is missing.
    """
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    if not gemini_api_key:
        raise ValueError("ERROR: GEMINI_API_KEY not found. Please set it as an environment variable.")

    try:
        genai.configure(api_key=gemini_api_key)
        print("Google Generative AI API configured successfully.")
    except Exception as e:
        raise RuntimeError(f"Failed to configure Generative AI API: {e}")
