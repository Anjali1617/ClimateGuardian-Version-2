import subprocess
import sys
import os
import json
import time

def run_game():
    """Run the Ocean Guardian game as a separate process and return the score and any error message."""
    script = os.path.join(os.path.dirname(__file__), 'ocean_sustainability_game.py')
    score_file = os.path.join(os.path.dirname(__file__), 'ocean_guardian_score.json')
        
    # Remove old score file if it exists
    if os.path.exists(score_file):
        try:
            os.remove(score_file)
        except OSError as e:
            print(f"Warning: Could not remove old score file {score_file}: {e}")

    print(f"Attempting to launch game script: {script}")
    
    try:
        if not os.path.exists(script):
            print(f"ERROR: Game script not found at {script}")
            return 0

        custom_env = os.environ.copy()
        custom_env["PYTHONIOENCODING"] = "utf-8"

        # Run the game script and capture its output to help debug crashes
        result = subprocess.run(
            [sys.executable, script], 
            check=False, 
            capture_output=True, 
            text=True,
            encoding='utf-8', # Explicitly set encoding to avoid issues
            env=custom_env
        )

        # If the game script crashed, print its error output to the console
        if result.returncode != 0:
            print(f"--- ERROR running ocean_sustainability_game.py ---")
            print(f"STDERR:\n{result.stderr}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"--------------------------------------------------")
    except Exception as e:
        print(f"Game execution error: {e}")
    
    # Give it a moment to write the file
    time.sleep(1)
    
    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                data = json.load(f)
                # If the game was won (score > 0), award 10 points.
                if data.get('score', 0) > 0:
                    return 10
                return 0
        except Exception as e:
            print(f"Error reading score file: {e}")
            return 0
    else:
        return 0