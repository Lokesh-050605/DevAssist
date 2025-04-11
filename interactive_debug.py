from utils import speak
import subprocess

def interactive_debugging(suggestions):
    """Interactively guide the user through debugging suggestions."""
    error_category = suggestions.get("error_category", "Unknown")
    probable_causes = suggestions.get("probable_causes", [])
    step_by_step_fix = suggestions.get("step_by_step_fix", [])
    suggested_fix = suggestions.get("suggested_fix", "")
    auto_fix_command = suggestions.get("auto_fix_command", "")
    
    print(f"Debugging Error: {error_category}")
    speak(f"Debugging error: {error_category}")

    if probable_causes:
        print("Probable Causes:")
        speak("Here are the probable causes:")
        for i, cause in enumerate(probable_causes, 1):
            print(f"{i}. {cause}")
            speak(f"{i}. {cause}")

    if step_by_step_fix:
        print("Step-by-Step Fix:")
        speak("Here’s a step-by-step fix:")
        for i, step in enumerate(step_by_step_fix, 1):
            print(f"Step {i}: {step}")
            speak(f"Step {i}: {step}")
            response = input("Would you like to proceed with this step? (yes/no): ").lower()
            if response != "yes":
                speak("Skipping this step.")
                print("Skipping this step.")
                break

    if suggested_fix:
        print(f"Suggested Fix: {suggested_fix}")
        speak(f"Suggested fix: {suggested_fix}")
        response = input("Would you like to apply this fix? (yes/no): ").lower()
        if response == "yes":
            speak("Applying the suggested fix.")
            print("Applying fix...")
            if auto_fix_command:  # Execute the auto-fix command if provided
                try:
                    result = subprocess.run(auto_fix_command, shell=True, text=True, capture_output=True)
                    if result.returncode == 0:
                        speak("Fix applied successfully.")
                        print(f"Fix output: {result.stdout}")
                        return {"applied_fix": suggested_fix, "auto_fix_output": result.stdout}
                    else:
                        speak("Failed to apply fix.")
                        print(f"Fix error: {result.stderr}")
                        return {"applied_fix": suggested_fix, "error": result.stderr}
                except Exception as e:
                    speak("Error while applying fix.")
                    print(f"Error applying fix: {str(e)}")
                    return {"applied_fix": suggested_fix, "error": str(e)}
            return {"applied_fix": suggested_fix}
        else:
            speak("Fix not applied.")
            print("Fix not applied.")

    if auto_fix_command and not suggested_fix:  # Fallback if only auto_fix_command is provided
        print(f"Auto-Fix Command: {auto_fix_command}")
        speak(f"I can run this command to fix it: {auto_fix_command}")
        response = input("Run auto-fix command? (yes/no): ").lower()
        if response == "yes":
            try:
                result = subprocess.run(auto_fix_command, shell=True, text=True, capture_output=True)
                if result.returncode == 0:
                    speak("Auto-fix applied successfully.")
                    print(f"Auto-fix output: {result.stdout}")
                    return {"auto_fix_applied": auto_fix_command, "output": result.stdout}
                else:
                    speak("Auto-fix failed.")
                    print(f"Auto-fix error: {result.stderr}")
                    return {"auto_fix_failed": auto_fix_command, "error": result.stderr}
            except Exception as e:
                speak("Error while applying auto-fix.")
                print(f"Error applying auto-fix: {str(e)}")
                return {"auto_fix_failed": auto_fix_command, "error": str(e)}

    speak("Debugging complete. No fixes applied.")
    return {"status": "no_fixes_applied"}