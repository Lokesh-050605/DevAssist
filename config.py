import google.generativeai as genai

# Load API Key
GEMINI_API_KEY = "AIzaSyB-ibPnz6E9rW-I4jfME879TCulX-yt5Dg"
if not GEMINI_API_KEY:
    raise ValueError("ERROR: GEMINI_API_KEY not found. Set it as an environment variable.")

# Configure Google Generative AI
def configure_api():
    genai.configure(api_key=GEMINI_API_KEY)

# configure_api()

# for model in genai.list_models():
#     print(model.name)
