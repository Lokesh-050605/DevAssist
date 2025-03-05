import os
import shutil
import subprocess
import time
import pynvim
import pyttsx3
import google.generativeai as genai

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    """Speaks the provided text for accessibility."""
    engine.say(text)
    engine.runAndWait()

def open_nvim_with_assistance():
    """
    Opens Neovim in a new terminal and provides AI-powered coding assistance.
    """
    file_path = "programming_session.py"

    # Ensure the file exists
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("# Start coding here...\n")

    print(f"Opening Neovim for coding assistance...")
    speak("Opening Neovim for coding assistance.")

    # Check if Neovim is installed
    if not shutil.which("nvim"):
        print("Error: Neovim is not installed or not found in PATH.")
        speak("Neovim is not installed. Please install Neovim.")
        return

    # Launch Neovim in a new terminal
    try:
        subprocess.Popen(["cmd", "/k", f"nvim {file_path}"], shell=True)
        time.sleep(2)  # Allow Neovim to start
    except Exception as e:
        print(f"ERROR: Failed to launch Neovim - {e}")
        speak("Failed to open Neovim.")
        return

    # Attach to Neovim session
    try:
        nvim = pynvim.attach("socket", path="/tmp/nvim")
        speak("Neovim is open. Start coding. I will assist you.")
        monitor_nvim_for_code(nvim)
    except Exception as e:
        print(f"ERROR: Could not connect to Neovim - {e}")
        speak("Could not connect to Neovim session.")
        return

def monitor_nvim_for_code(nvim):
    """
    Monitors Neovim buffer for changes and provides AI coding suggestions.
    """
    last_content = ""  # Stores previous buffer content

    while True:
        try:
            buffer_content = "\n".join(nvim.current.buffer[:])

            if buffer_content != last_content:  # Detects new code input
                last_content = buffer_content
                print("\nUser wrote new code. Fetching AI suggestions...\n")
                speak("Fetching AI suggestions for your code.")

                suggestion = get_ai_suggestion(buffer_content)
                if suggestion:
                    # Insert AI suggestion as a comment in Neovim
                    nvim.current.buffer.append(f"# AI Suggestion: {suggestion}")
                    speak(f"Here is a suggestion: {suggestion}")

            time.sleep(5)  # Check for changes every 5 seconds
        except Exception as e:
            print(f"ERROR: {e}")
            speak("An error occurred while monitoring Neovim.")
            break  # Stop monitoring on failure

def get_ai_suggestion(code_snippet):
    """
    Sends the code snippet to Google Generative AI and returns a suggestion.
    """
    prompt = f"""
    You are an AI coding assistant. Analyze the following Python code and suggest improvements:
    
    {code_snippet}

    Provide concise and useful feedback.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)

        if not response or not response.text:
            return "No suggestions available."

        return response.text.strip()
    except Exception as e:
        print(f"ERROR: Failed to generate AI suggestion - {e}")
        speak("AI assistance is currently unavailable.")
        return "AI assistance unavailable."

if __name__ == "__main__":
    open_nvim_with_assistance()
