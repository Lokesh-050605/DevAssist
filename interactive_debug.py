from utils import speak
import subprocess

def interactive_debugging(suggestions):
    """Interactively guide the user through debugging suggestions."""

    print(f"Debugging Suggestions:{suggestions}")
    error_category = suggestions.get("error_category", "Unknown")
    probable_causes = suggestions.get("probable_causes", [])
    step_by_step_fix = suggestions.get("step_by_step_fix", [])
    suggested_fix = suggestions.get("suggested_fix", "")
    auto_fix_command = suggestions.get("auto_fix_command", "")
    
    print(f"Debugging Error: {error_category}")
    speak(f"Debugging error: {error_category}")

    if probable_causes:
        print("\nProbable Causes:")
        speak("Here are the probable causes:")
        for i, cause in enumerate(probable_causes, 1):
            print(f"{i}. {cause}")
            speak(f"{i}. {cause}")

    # Try auto-fix first if available
    if auto_fix_command:
        print(f"\nAuto-Fix Command Available: {auto_fix_command}")
        speak("An automatic fix is available. Would you like me to try it?")
        response = input("Do you want to apply the auto-fix now? (yes/no): ").lower()
        if response == "yes":
            speak("Trying to apply auto-fix.")
            try:
                result = subprocess.run(auto_fix_command, shell=True, text=True, capture_output=True)
                if result.returncode == 0:
                    speak("Auto-fix applied successfully.")
                    print(f"\nAuto-fix Output:\n{result.stdout}")
                    return {"auto_fix_applied": auto_fix_command, "output": result.stdout}
                else:
                    speak("Auto-fix failed. Let's try a manual fix.")
                    print(f"\nAuto-fix failed:\n{result.stderr}")
            except Exception as e:
                speak("An error occurred while applying the fix.")
                print(f"\nError applying auto-fix: {str(e)}")
        else:
            speak("Okay, proceeding with manual steps.")

    # Proceed with step-by-step manual fix
    if step_by_step_fix:
        print("\nManual Step-by-Step Fix:")
        speak("Here is a step-by-step fix.")
        for i, step in enumerate(step_by_step_fix, 1):
            print(f"Step {i}: {step}")
            speak(f"Step {i}: {step}")
            

    # Final suggestion if available
    if suggested_fix:
        print(f"\nFinal Suggested Fix:\n{suggested_fix}")
        speak("Here is a final suggestion to fix the issue.")
        speak(suggested_fix)

    speak("Debugging complete.")
    return {"status": "debugging_complete"}
