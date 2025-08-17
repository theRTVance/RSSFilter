#!/usr/bin/env python3

import os
import subprocess
import sys
import logging # 1. Import the logging module

# --- Configuration ---
SCRIPT_DIR = "Your Scipts Directory Here" #<------ Place you RSSFilter file directory here
PYTHON_FILTER_SCRIPTS = [
    #"Name Your Files.py",
    #"Filterous Maximus_a Ancient Roman Filter.py",
    #"More filtering than coffee.py",
    #"Honey, I filtered the kids.py",
    #"Star Wars ep1 Never should have existed, just the facts nothing filtered.py"
]
LOG_DIR = "Error: Log needs location" #<--- Where you want the log files to be writen
LOG_FILE_NAME = "logs.did" #<-- It .did the logs didn't it. Yes this is why I am not invited to parties.
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)
# --------------------

def dispatch_filters(logger): # 4. The launching function now accepts a logger
    """Launches the filter scripts and logs all actions."""
    logger.info("Dispatching filter scripts...") # 5. Log the start of the process
    pids = []
    for script_name in PYTHON_FILTER_SCRIPTS:
        full_script_path = os.path.join(SCRIPT_DIR, script_name)
        if not os.path.exists(full_script_path):
            logger.error(f"ERROR: Filter script not found: {full_script_path}. Skipping.")
            continue
        try:
            logger.info(f"Launching {script_name}...") # 6. Log each script launch
            process = subprocess.Popen(['python3', full_script_path])
            pids.append(process)
        except OSError as e:
            logger.error(f"ERROR: Could not launch {script_name}: {e}")
    
    logger.info("Waiting for filter scripts to complete...") # 7. Log the waiting period
    for p in pids:
        p.wait()
    logger.info("All filter scripts have completed.") # 8. Log the completion

def main():
    # 2. Configure the logging system at the beginning of the main function
    os.makedirs(LOG_DIR, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, # Set the logging level to INFO
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE_PATH, mode='w', encoding='utf-8')
        ]
    )
    logger = logging.getLogger(__name__)

    # 3. Call the launching function, passing the logger object
    dispatch_filters(logger)

if __name__ == "__main__":
    main()
