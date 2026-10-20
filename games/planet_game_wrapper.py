import subprocess
import sys
import os
import json
import time

def run_game():
    """Run the Planet Earth Sustainability game as a separate process and return the score."""
    script = os.path.join(os.path.dirname(__file__), 'planet_game.py')
    score_file = os.path.join(os.path.dirname(__file__), 'planet_game_score.json')
    
    # Remove old score file if it exists to ensure fresh score
    if os.path.exists(score_file):
        try:
            os.remove(score_file)
        except OSError as e:
            print(f"Warning: Could not remove old score file {score_file}: {e}")

    try:
        if not os.path.exists(script):
            print(f"ERROR: Game script not found at {script}")
            return 0

        subprocess.run([sys.executable, script], check=False)
    except Exception as e:
        print(f"Game execution error: {e}")
    
    time.sleep(1) # Give the file system a moment to write the JSON 
    
    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                data = json.load(f)
                result = data.get('result', 'quit')
                
                # Win condition: +20 points
                if result in ("win", "exit_win"):
                    return 20
                # Lose condition: -10 points
                elif result in ("lose", "exit_lose"):
                    return -10
                # Default (quit mid-game): 0 points
                else:
                    return 0
        except Exception as e:
            print(f"Error reading score file: {e}")
            return 0
    else:
        return 0