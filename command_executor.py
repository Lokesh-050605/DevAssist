import os

def execute_command(command):
    """Executes the generated Windows terminal command."""
    try:
        os.system(command)
    except Exception as e:
        print(f"ERROR: Failed to execute command - {e}")
