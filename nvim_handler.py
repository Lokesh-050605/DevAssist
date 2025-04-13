import pynvim
import subprocess
import os
import time
from utils import speak  # Assuming you have a 'utils.py' with a 'speak' function

class NvimHandler:
    def __init__(self):
        self.nvim_process = None
        self.nvim = None
        self.nvim_path = os.path.join("C:\\Program Files\\nvim-win64\\bin", "nvim.exe")
        if not os.path.exists(self.nvim_path):
            self.nvim_path = "nvim"
        self.socket_path = "\\\\.\\pipe\\nvim-pipe"  # Windows named pipe

    def start_nvim(self, filename=None):
        if self.nvim_process is None:
            try:
                # Start Neovim in a new console window with a server
                cmd = [self.nvim_path, "--listen", self.socket_path]
                if filename:
                    cmd.append(filename)
                self.nvim_process = subprocess.Popen(
                    cmd,
                    shell=False,  # Avoid shell inheritance
                    creationflags=subprocess.CREATE_NEW_CONSOLE  # New window
                )
                # Wait briefly for server to start
                time.sleep(1)
                # Connect to Neovim instance
                self.nvim = pynvim.attach('socket', path=self.socket_path)
                speak("Neovim started in a new window.")
                print("Neovim started in a new window.")
            except FileNotFoundError:
                speak("Neovim not found. Please ensure Neovim is installed and added to your PATH.")
                print("Error: Neovim not found. Install Neovim or update PATH.")
                raise
            except Exception as e:
                speak(f"Failed to start Neovim: {str(e)}")
                print(f"Error starting Neovim: {str(e)}")
                raise

    def stop_nvim(self):
        if self.nvim:
            try:
                # Force quit all buffers without saving or prompting
                self.nvim.command("wq")
                self.nvim.close()
            except Exception as e:
                print(f"Error quitting Neovim gracefully: {e}")
            self.nvim = None

        if self.nvim_process:
            try:
                # Send terminate signal and give it time to exit
                self.nvim_process.terminate()
                self.nvim_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("Neovim process did not terminate gracefully, forcing kill...")
                self.nvim_process.kill()  # Force kill if terminate fails
                self.nvim_process.wait(timeout=5)
            except Exception as e:
                print(f"Error terminating Neovim process: {e}")
            self.nvim_process = None

        speak("Neovim stopped.")
        print("Neovim stopped.")


    def open_file(self, filename):
        if not os.path.exists(filename):
            speak(f"File {filename} does not exist.")
            return {"error": f"File {filename} not found"}
        self.start_nvim(filename)
        speak(f"Opened {filename} in Neovim.")
        print(f"Opened {filename} in Neovim.")
        return {"status": "file_opened", "filename": filename, "file_handler":self}

    def insert_line(self, filename, content, line):
        if not self.nvim:
            self.start_nvim(filename)
        else:
            self.nvim.command(f"e {filename}")
        
        buffer = self.nvim.current.buffer
        total_lines = len(buffer)

        if 1 <= line <= total_lines + 1:
            buffer[line - 1:line - 1] = content.splitlines()
            self.nvim.command("w")
            speak(f"Inserted content at line {line} in {filename}.")
            print(f"Inserted content at line {line} in {filename}.")
            return {"status": "line_inserted", "filename": filename, "line": line, "content": content}
        else:
            speak(f"Invalid line number {line}. File has only {total_lines} lines.")
            print(f"Invalid line number {line}. File has only {total_lines} lines.")
            return {"status": "invalid_line", "filename": filename, "line": line}


    # def find_in_file(self, filename, target, gemini_response):
    #     if not self.nvim:
    #         self.start_nvim(filename)
    #     else:
    #         self.nvim.command(f"e {filename}")
    #     file_content = "\n".join(self.nvim.current.buffer[:])
    #     if "general_response" in gemini_response:
    #         line_number = int(gemini_response["general_response"])
    #     else:
    #         for i, line in enumerate(self.nvim.current.buffer, 1):
    #             if target in line:
    #                 line_number = i
    #                 break
    #         else:
    #             line_number = 1
    #     self.nvim.command(f":{line_number}")
    #     speak(f"Moved cursor to line {line_number} for '{target}' in {filename}.")
    #     print(f"Moved cursor to line {line_number} for '{target}' in {filename}.")
    #     return {"status": "cursor_moved", "filename": filename, "line": line_number}

    def find_function(self, filename, function_name, line_no):
        if not self.nvim:
            self.start_nvim(filename)
        else:
            self.nvim.command(f"e {filename}")
        
        buffer_length = len(self.nvim.current.buffer[:])
        
        if 1 <= line_no <= buffer_length:
            self.nvim.command(f":{line_no}")
            speak(f"Moved cursor to line {line_no} for '{function_name}' in {filename}.")
            print(f"Moved cursor to line {line_no} for '{function_name}' in {filename}.")
            return {"status": "cursor_moved", "filename": filename, "line": line_no}
        else:
            speak(f"Line {line_no} is out of range for {filename}.")
            print(f"Line {line_no} is out of range for {filename}.")
            return {"status": "invalid_line", "filename": filename, "line": line_no}

    def append_to_file(self, filename, content):
        if not self.nvim:
            self.start_nvim(filename)
        else:
            self.nvim.command(f"e {filename}")
        self.nvim.current.buffer.append(content.splitlines())
        self.nvim.command("w")
        speak(f"Appended '{content}' to the end of {filename}.")
        print(f"Appended '{content}' to the end of {filename}.")
        return {"status": "content_appended", "filename": filename, "content": content}

# Driver Code
if __name__ == "__main__":
    nvim_handler = NvimHandler()

    # Create a test file
    test_filename = "test.txt"
    

    # Open the file
    nvim_handler.open_file(test_filename)

    # Insert a line
    nvim_handler.insert_line(test_filename, "Inserted line.", 2)

    # Find a line
    gemini_response = {} # or gemini_response={"general_response":3}
    nvim_handler.find_in_file(test_filename, "line 3", gemini_response)

    # Append to the file
    nvim_handler.append_to_file(test_filename, "Appended content.")

    # Stop Neovim
    nvim_handler.stop_nvim()
