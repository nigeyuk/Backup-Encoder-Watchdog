# main.py

import time
import logging
from logging_setup import setup_logging
from notifications import notify_online, send_status_update, notify_discord
import checks  # Import the checks module
from config import WAIT_TIME_BEFORE_BACKUP, DISCORD_UPDATE_INTERVAL, AWS_BACKUP_INSTANCE_ID
from subprocess import run

def start_backup_instance():
    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting backup instance...")
        print("Starting backup instance...")  # Console output
        command = f"aws ec2 start-instances --instance-ids {AWS_BACKUP_INSTANCE_ID}"
        result = run(command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Backup instance {AWS_BACKUP_INSTANCE_ID} started successfully.")
            print(f"Backup instance {AWS_BACKUP_INSTANCE_ID} started successfully.")  # Console output
            notify_discord(f"Backup instance {AWS_BACKUP_INSTANCE_ID} started successfully.")
        else:
            logger.error(f"Failed to start backup instance: {result.stderr}")
            print(f"Failed to start backup instance: {result.stderr}")  # Console output
            notify_discord(f"Failed to start backup instance: {result.stderr}")

    except Exception as e:
        logger.error(f"Error starting backup instance: {e}")
        print(f"Error starting backup instance: {e}")  # Console output
        notify_discord(f"Error starting backup instance: {e}")

def main():
    logger = logging.getLogger(__name__)
    notify_online()  # Send notification when the bot comes online

    logger.info("Entering main loop...")
    print("Entering main loop...")  # Console output
    last_update_time = time.time()
    while True:
        logger.info("Checking statuses...")
        print("Checking statuses...")  # Console output

        statuses = {
            'icecast': checks.check_icecast_sources(),
            'liquidsoap': checks.check_liquidsoap_cpu(),
            'ts_file_count': checks.check_ts_file_count(),
            'hls_old_files': checks.check_hls_directory()
        }

        # Access hls_ts_file_count and liquidsoap_pid from checks module
        hls_ts_file_count = checks.hls_ts_file_count
        liquidsoap_pid = checks.liquidsoap_pid

        # Check for failures
        failed_checks = sum(status == "fail" for status in statuses.values())
        if failed_checks >= 2:
            notify_discord("Warning: 2 or more parameters are in a failed state. Bringing up the backup instance.")
            start_backup_instance()
            time.sleep(WAIT_TIME_BEFORE_BACKUP)

        # Send periodic status update based on DISCORD_UPDATE_INTERVAL
        current_time = time.time()
        if current_time - last_update_time >= DISCORD_UPDATE_INTERVAL:
            send_status_update(statuses, hls_ts_file_count, liquidsoap_pid)  # Pass liquidsoap_pid here
            last_update_time = current_time
            logger.info("Status update sent.")
            print("Status update sent.")  # Console output

        time.sleep(300)  # Sleep for 5 minutes

if __name__ == "__main__":
    logger = setup_logging()
    main()

