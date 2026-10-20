import subprocess
import sys
import os
import json
import time

def run_game():
    """Run the Eco Defender game as a separate process and return the score."""
    script = os.path.join(os.path.dirname(__file__), 'eco_defender.py')
    score_file = os.path.join(os.path.dirname(__file__), 'eco_defender_score.json')
    
    # Remove old score file if it exists to ensure a fresh score
    if os.path.exists(score_file):
        try:
            os.remove(score_file)
        except OSError as e:
            print(f"Warning: Could not remove old score file {score_file}: {e}")

    try:
        if not os.path.exists(script):
            # Raise an error so Streamlit shows it on the screen
            raise FileNotFoundError(f"Missing file! Please place 'eco_defender.py' inside the 'games' folder.")
            
        # Force UTF-8 encoding so emojis in print statements don't crash Windows
        custom_env = os.environ.copy()
        custom_env["PYTHONIOENCODING"] = "utf-8"

        # Capture output to help debug if it crashes
        result = subprocess.run(
            [sys.executable, script], 
            check=False, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            env=custom_env
        )
        if result.returncode != 0:
            print(f"--- ERROR running eco_defender.py ---\n{result.stderr}\n-------------------")
            raise RuntimeError(f"Game crashed! Details:\n{result.stderr}")
    except Exception as e:
        print(f"Game execution error: {e}")
        raise e # Pass the error up to the Streamlit app

    # Poll for the score file to appear, with a timeout of 5 seconds.
    # This is more robust than a fixed time.sleep().
    timeout = 5
    start_time = time.time()
    while not os.path.exists(score_file):
        if time.time() - start_time > timeout:
            print(f"Error: Score file '{score_file}' not found after {timeout} seconds.")
            return 0
        time.sleep(0.1)

    if os.path.exists(score_file):
        try:
            with open(score_file, 'r') as f:
                data = json.load(f)
                result = data.get('result', 'quit')
                difficulty = data.get('difficulty', 'medium')
                return data.get('score', 0) # Return the actual score from the game
        except Exception as e:
            print(f"Error reading score file: {e}")
            return 0
    return 0