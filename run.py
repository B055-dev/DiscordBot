# Copyright (c) 2025 B055
# SPDX-License-Identifier: MIT
# See LICENSE file for details.

import os
import sys
import subprocess
import time

def main():
    """Run the bot with automatic restart on crash."""
    print("Starting B055 Discord Bot...")
    
    while True:
        try:
            # Run the bot
            process = subprocess.Popen([sys.executable, "main.py"])
            process.wait()
            
            # If the process exited with code 0, it was a clean shutdown
            if process.returncode == 0:
                print("Bot shutdown cleanly. Exiting.")
                break
            
            # Otherwise, it crashed
            print("Bot crashed. Restarting in 5 seconds...")
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Shutting down...")
            if 'process' in locals():
                process.terminate()
            break
        except Exception as e:
            print(f"Error running bot: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
 
