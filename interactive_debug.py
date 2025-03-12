from query_generator import execute_command
from utils import speak

def interactive_debugging(debug_data):
    """Guides the user through the debugging process interactively."""
    
    # Speech Output
    speak("Debugging Assistant Activated")
    print("\n🔍 Debugging Assistant 🔍")
    
    # Display Error Category
    error_type = debug_data.get("error_category", "Unknown Error")
    print(f"📌 Error Type: {error_type}\n")
    speak(f"Error detected: {error_type}")

    # Show probable causes
    probable_causes = debug_data.get("probable_causes", [])
    if probable_causes:
        print("⚠️ Possible Causes:")
        speak("Possible causes include the following:")
        for cause in probable_causes:
            print(f" - {cause}")
        speak("Would you like me to read them out loud? (yes/no)")
        if input("Read causes out loud? (yes/no): ").strip().lower() == "yes":
            for cause in probable_causes:
                speak(cause)

    # If there's a direct fix, suggest it first
    auto_fix = debug_data.get("auto_fix_command")
    if auto_fix:
        print(f"\n💡 Suggested Fix: Run `{auto_fix}`")
        speak("A direct fix is available. Would you like to apply it?")
        execute_fix = input(f"Would you like to run: `{auto_fix}`? (yes/no): ").strip().lower()
        if execute_fix == "yes":
            op = execute_command(auto_fix)
            if op:
                print("\n✅ Fix applied successfully! \n" + op)
                speak("Fix applied successfully.")
                return
            else:
                print("\n❌ Failed to execute the fix. Error:")
                print(op)  # Display exact error message
                speak("Fix execution failed. Try running it manually.")

    # Step-by-step debugging
    step_by_step_fix = debug_data.get("step_by_step_fix", [])
    if step_by_step_fix:
        print("\n🛠 Let's fix this step by step!")
        for step in step_by_step_fix:
            response = input(f"\n{step} (yes/no/skip all): ").strip().lower()
            if response == "yes":
                continue  # Move to the next step
            elif response == "skip all":
                print("Skipping all steps.")
                break
            else:
                print("Skipping this step.")
                continue  # Continue allowing other steps

    # Alternative solutions
    alternative_solutions = debug_data.get("alternative_solutions", [])
    if alternative_solutions:
        print("\n🔄 Alternative Solutions:")
        for alt in alternative_solutions:
            print(f" - {alt}")

    # Preventive measures
    preventive_measures = debug_data.get("preventive_measures", [])
    if preventive_measures:
        print("\n🛑 Best Practices to Avoid This Issue in the Future:")
        for measure in preventive_measures:
            print(f" - {measure}")

    print("\nDebugging session complete! Let me know if you need more help.\n")
    speak("Debugging complete. Let me know if you need more help.")
