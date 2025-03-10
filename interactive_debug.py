from query_generator import execute_command
from utils import speak


def interactive_debugging(debug_data):
    """Guides the user through the debugging process interactively."""
    
    # Speech Output
    speak("Debugging Assistant Activated")
    print("\n🔍 Debugging Assistant 🔍")
    
    # Display Error Category
    error_type = debug_data.get("error_category")
    print(f"📌 Error Type: {error_type}\n")
    speak(f"Error detected: {error_type}")

    # Show probable causes
    print("⚠️ Possible Causes:")
    for cause in debug_data["probable_causes"]:
        print(f" - {cause}")
        speak(cause)

    # If there's a direct fix, suggest it first
    auto_fix = debug_data["auto_fix_command"]
    if auto_fix:
        print(f"\n💡 Suggested Fix:** Run `{auto_fix}`")
        speak("A direct fix is available. Would you like to apply it?")
        execute_fix = input(f"Would you like to run: `{auto_fix}`? (yes/no): ").strip().lower()
        if execute_fix == "yes":
            op = execute_command(auto_fix)
            if op:
                print("\n✅ Fix applied successfully! \n"+op)
                speak("Fix applied successfully."+op)
                print("\nClosing Debugging Assistant.")
                speak("Closing Debugging Assistant.")
                return
            else:
                print("\n❌ Failed to execute the fix. Try running it manually.")
                speak("Fix execution failed. Try running it manually.")

    # If no direct fix, proceed with step-by-step debugging
    print("\n🛠 Let's fix this step by step!")
    for step in debug_data["step_by_step_fix"]:
        response = input(f"\n{step} (yes/no): ").strip().lower()
        if response == "yes":
            continue  # Move to the next step
        else:
            print("Skipping this step.")
            break

    # Alternative solutions
    if debug_data["alternative_solutions"]:
        print("\n🔄 Alternative Solutions:")
        for alt in debug_data["alternative_solutions"]:
            print(f" - {alt}")
            speak(alt)

    # Preventive measures
    if debug_data["preventive_measures"]:
        print("\n🛑 Best Practices to Avoid This Issue in the Future:")
        for measure in debug_data["preventive_measures"]:
            print(f" - {measure}")
            speak(measure)

    print("\nDebugging session complete! Let me know if you need more help.\n")
    speak("Debugging complete. Let me know if you need more help.")
