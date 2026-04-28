from core.command import run_sudo_cmd
from src.cli.ui.cli_utils import print_header, print_info, print_newline, Spinner

import time

def main():
    print_header("Testing stuff", details="Nothing to show here")
    print_newline(2)
    
    with Spinner(message="Doing something....") as spinner:
        time.sleep(2)

        rc = run_sudo_cmd(command="sudo pacman -Syu --noconfirm", spinner=spinner)

        
    
    # print_info(text="Done", details=f"Process exited with returncode {rc}")
    print_newline(1)
    print_info("Testing done!")
