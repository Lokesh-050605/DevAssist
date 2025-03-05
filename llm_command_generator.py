import pyttsx3

# Importing necessary functions safely
try:
    from config import configure_api
    from command_generator import generate_command
    from command_executor import execute_command
    from neovim_assistant import open_nvim_with_assistance  
except ImportError as e:
    print(f"Module Import Error: {e}")
    exit(1)

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    """Speaks the provided text for accessibility."""
    if text:
        engine.say(text)
        engine.runAndWait()

def main():
    try:
        configure_api()
        print("API configured successfully!")
    except Exception as e:
        print(f"Error configuring API: {e}")
        return  # Exit if API configuration fails

    while True:
        try:
            user_input = input("\nEnter your task (or type 'exit' to quit): ").strip().lower()
            
            if not user_input:
                print("Please enter a valid command.")
                continue
            
            if user_input == "exit":
                print("Exiting...")
                speak("Exiting Dev Assist")
                break

            if "open vim" in user_input or "open neovim" in user_input:
                print("Opening Neovim with AI assistance...")
                speak("Opening Neovim with AI assistance")
                open_nvim_with_assistance()
                continue  

            command = generate_command(user_input)
            if not command:
                print("Could not generate a command. Please try again.")
                continue
            
            print(f"Generated Command: {command}")
            speak(f"The generated command is {command}")

            execute = input("Run this command? (yes/no): ").strip().lower()
            if execute == "yes":
                speak("Executing the command now")
                execute_command(command)
            else:
                print("Command execution cancelled.")

        except Exception as e:
            print(f"Error: {e}")
            speak("An error occurred. Please try again.")

if __name__ == "__main__":
    main()
