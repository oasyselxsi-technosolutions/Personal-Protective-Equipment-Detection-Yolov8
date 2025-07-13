#!/usr/bin/env python3
"""
Run Flask app with comprehensive logging to file.
Usage: python run_flask_with_logging.py [port]
Example: python run_flask_with_logging.py 5000
"""

import os
import sys
import subprocess
import signal
import logging
from datetime import datetime

def setup_runtime_logging():
    """Set up logging for the runtime script."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - RUNTIME - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'runtime.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_runtime_logging()
    
    # Get port from command line or default to 5000
    port = sys.argv[1] if len(sys.argv) > 1 else "5000"
    
    logger.info("="*80)
    logger.info("STARTING FLASK PPE DETECTION APP WITH LOGGING")
    logger.info("="*80)
    logger.info(f"Port: {port}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    
    # Ensure logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")
        logger.info("Created logs directory")
    
    # Prepare environment variables
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'  # Ensure immediate output
    
    try:
        # Start Flask app
        cmd = [sys.executable, "flaskapp.py", port]
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=env,
            bufsize=1  # Line buffered
        )
        
        logger.info(f"Flask process started with PID: {process.pid}")
        
        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            logger.info("Interrupt received, stopping Flask app...")
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Process didn't terminate gracefully, killing...")
                process.kill()
            logger.info("Flask app stopped")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Stream output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                # Also log to file (already handled by Flask's logging setup)
        
        rc = process.poll()
        logger.info(f"Flask process ended with return code: {rc}")
        
    except Exception as e:
        logger.error(f"Error running Flask app: {str(e)}")
        logger.exception("Full exception details:")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
