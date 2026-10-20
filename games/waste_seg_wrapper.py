import subprocess
import sys
import os
import json
import time

def run_game():
    """Run the Waste Segregation game as a separate process and return the score."""
    script = os.path.join(os.path.dirname(__file__), 'waste_segregation.py')
    score_file = os.path.join(os.path.dirname(__file__), 'waste_segregation_score.json')
    
    # Remove old score file if it exists
    if os.path.exists(score_file):
        os.remove(score_file)
    
    try:
        subprocess.run([sys.executable, script], check=False)  # Don't check for errors
    except Exception as e:
        print(f"Game execution error: {e}")
    
    # Always try to read the score, whether game succeeded or failed
    time.sleep(1)  # Give it a moment to write the file
    
    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                data = json.load(f)
                game_score = data.get('score', 0)
                print(f"Game score read: {game_score}")
                return game_score
        except Exception as e:
            print(f"Error reading score file: {e}")
            return 0
    else:
        print(f"Score file not found at {score_file}")
        return 0
