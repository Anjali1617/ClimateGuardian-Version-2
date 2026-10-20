import subprocess
import sys
import os
import json
import time

def run_game():
    """Run the Eco Puzzle 3D game as a separate process and return the score."""
    script = os.path.join(os.path.dirname(__file__), 'eco_puzzle_game.py')
    score_file = os.path.join(os.path.dirname(__file__), 'eco_puzzle_score.json')
    
    # Remove old score file if it exists to ensure a fresh score
    if os.path.exists(score_file):
        try:
            os.remove(score_file)
        except OSError as e:
            print(f"Warning: Could not remove old score file {score_file}: {e}")

    try:
        if not os.path.exists(script):
            raise FileNotFoundError(f"Missing file! Please place 'eco_puzzle_game.py' inside the 'games' folder.")
            
        custom_env = os.environ.copy()
        custom_env["PYTHONIOENCODING"] = "utf-8"

        result = subprocess.run(
            [sys.executable, script], 
            check=False, 
            env=custom_env
        )
    except Exception as e:
        print(f"Game execution error: {e}")
    
    time.sleep(1)
    
    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                return json.load(f).get('score', 0)
        except Exception:
            return 0
    return 0