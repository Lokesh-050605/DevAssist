from config import configure_api
from command_generator import generate_command
from command_executor import execute_command

def main():
    configure_api()  # Initialize API

    while True:
        user_input = input("\nEnter your task (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        command = generate_command(user_input)
        print(f"Generated Command: {command}")

        # Execute the command (optional)
        execute = input("Run this command? (yes/no): ").strip().lower()
        if execute == "yes":
            execute_command(command)

if __name__ == "__main__":
    main()
