from command_processor import process_command

if __name__ == "__main__":
    cmd = input(">> ")
    process_command(cmd)
    #process_command("commit and push changes to git")