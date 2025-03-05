import os
import google.generativeai as genai
from utils import extract_command

def generate_command(user_input):
    """
    Uses Gemini AI to convert natural language input into a valid terminal command.
    Ensures all responses are executable and correctly formatted.
    """

    prompt = f"""
    You are a command-line assistant that converts natural language instructions into **fully executable terminal commands**.

    **Rules:**
    - If the user wants to **edit a file**, return `"nvim filename.extension"`.
    - If the user wants to **run a program**, generate the correct command based on the **file extension**.
    - If it's a **Python (`.py`)** file, return `"python filename.py"`.
    - If it's a **C (`.c`)** file, return `"gcc filename.c -o filename && ./filename"`.
    - If it's a **C++ (`.cpp`)** file, return `"g++ filename.cpp -o filename && ./filename"`.
    - If it's a **Java (`.java`)** file, return `"javac filename.java && java filename"` (ensure correct execution).
    - If it's a **JavaScript (`.js`)** file, return `"node filename.js"`.
    - If it's a **Go (`.go`)** file, return `"go run filename.go"`.
    - If it's a **Shell Script (`.sh`)**, return `"bash filename.sh"`.
    - If it's a **directory navigation** command, use `cd directory_name`.
    - The system is **Windows 10**, so ensure commands are compatible.

    **Examples:**
    - **"Edit main.py"** → `nvim main.py`
    - **"Run test.py"** → `python test.py`
    - **"Compile and execute program.c"** → `gcc program.c -o program && ./program`
    - **"Compile and run Java file sample.java"** → `javac sample.java && java sample`
    - **"Navigate to Documents folder"** → `cd Documents`
    - **"Open the python file config"** → `nvim config.py`
    - **"open the file config.py"** → `nvim config.py`
    - **"edit the java file sample"** → `nvim sample.java`

    **Instruction:** {user_input}  
    **Command:**
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)

        if not response or not response.text:
            return "ERROR: No response from AI."

        command = extract_command(response.text)

        # Auto-correct AI response if necessary
        command = enforce_correct_command(user_input, command)

        return command if command.strip() else "ERROR: No valid command generated."

    except Exception as e:
        return f"ERROR: Failed to generate command - {e}"

def enforce_correct_command(user_input, command):
    """
    Ensures AI-generated commands are correctly formatted based on file extensions.
    """
    file_extensions = {
        ".py": "python {}",
        ".java": "javac {} && java {}",
        ".c": "gcc {} -o {} && {}",
        ".cpp": "g++ {} -o {} && {}",
        ".js": "node {}",
        ".go": "go run {}",
        ".sh": "bash {}",
    }

    words = user_input.split()
    for word in words:
        for ext, cmd in file_extensions.items():
            if word.endswith(ext):
                filename = word.replace(ext, "")
                if "{}" in cmd:
                    return cmd.format(word, filename, filename)  # Format for compiled languages
                return cmd.format(word)  # Format for interpreted languages

    return command  # Return AI response if no modification is needed
