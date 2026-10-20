import subprocess
import sys
import os
import json
import time

def run_game():
    """Run the Eco Cricket game as a separate process and return the score."""
    script = os.path.join(os.path.dirname(__file__), 'eco_cricket_game.py')
    score_file = os.path.join(os.path.dirname(__file__), 'eco_cricket_score.json')
    
    # Remove old score file if it exists
    if os.path.exists(score_file):
        try:
            os.remove(score_file)
        except OSError as e:
            print(f"Warning: Could not remove old score file {score_file}: {e}")
    
    try:
        # Run the game script and capture its output to help debug crashes
        result = subprocess.run(
            [sys.executable, script], 
            check=False, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )

        # If the game script crashed, print its error output to the console
        if result.returncode != 0:
            print(f"--- ERROR running eco_cricket_game.py ---")
            print(f"STDERR:\n{result.stderr}")
            print(f"STDOUT:\n{result.stdout}")
            print(f"-------------------------------------------")
    except Exception as e:
        print(f"Game execution error: {e}")
    
    time.sleep(1) # Give it a moment to write the file
    
    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                return json.load(f).get('score', 0)
        except Exception as e:
            print(f"Error reading score file: {e}")
    return 0