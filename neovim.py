import os
import subprocess
import time

def open_nvim_in_new_terminal(file_path):
    """
    Opens Neovim in a new terminal and ensures the file exists.
    """
    # Ensure file exists before opening
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")  # Create an empty file

    print(f"Opening '{file_path}' in Neovim...")

    nvim_path = r"C:\Program Files\Neovim\bin\nvim.exe"  # Update path if needed
    subprocess.Popen(f'start cmd /k "{nvim_path} --listen localhost:6666 {file_path}"', shell=True)

    time.sleep(2)  # Give Neovim time to start

# Example usage
file_path = "test_file.txt"
open_nvim_in_new_terminal(file_path)
