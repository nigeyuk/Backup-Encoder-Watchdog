# notifications.py

import requests
import time
from config import ENABLE_DISCORD_UPDATES, DISCORD_WEBHOOK_URL
import logging

logger = logging.getLogger(__name__)

def notify_discord(message):
    """Send a simple notification message to Discord."""
    if not ENABLE_DISCORD_UPDATES:
        return
    try:
        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        logger.info(f"Discord notification sent: {response.status_code}")
    except Exception as e:
        logger.error(f"Error sending notification to Discord: {e}")
        print(f"Error sending notification to Discord: {e}")

def notify_online():
    """Notify Discord that the monitoring bot is online."""
    if not ENABLE_DISCORD_UPDATES:
        return
    try:
        restart_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        payload = {
            "content": f"The monitoring bot has restarted at {restart_time} and is now actively monitoring."
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload)
        logger.info("Online notification sent to Discord.")
        print("Online notification sent to Discord.")  # Console output
    except Exception as e:
        logger.error(f"Error sending online notification to Discord: {e}")
        print(f"Error sending online notification to Discord: {e}")

def send_status_update(statuses, hls_ts_file_count, liquidsoap_pid):
    """Send a detailed status update to Discord."""
    if not ENABLE_DISCORD_UPDATES:
        return
    logger.info("Sending status update to Discord...")
    try:
        last_checked_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        icecast_status = "Fail" if statuses['icecast'] == "fail" else "Pass"
        liquidsoap_status = "Fail" if statuses['liquidsoap'] == "fail" else "Pass"
        ts_file_count_status = "Fail" if statuses['ts_file_count'] == "fail" else "Pass"
        hls_old_files_status = "Fail" if statuses['hls_old_files'] == "fail" else "Pass"

        pass_count = sum(status == "Pass" for status in [
            icecast_status,
            liquidsoap_status,
            ts_file_count_status,
            hls_old_files_status
        ])
        fail_count = 4 - pass_count  # Total of 4 parameters

        # Include the Liquidsoap PID in the status update
        pid_info = liquidsoap_pid if liquidsoap_pid else "Not Running"

        embed = {
            "embeds": [
                {
                    "title": "Status Update",
                    "color": 7506394,
                    "fields": [
                        {"name": "Last Checked", "value": last_checked_time, "inline": False},
                        {"name": "Icecast Sources", "value": icecast_status, "inline": True},
                        {"name": "Liquidsoap CPU Usage", "value": f"{liquidsoap_status} (PID: {pid_info})", "inline": True},
                        {"name": "TS File Count", "value": ts_file_count_status, "inline": True},
                        {"name": "HLS Old Files", "value": hls_old_files_status, "inline": True},
                        {"name": "Current .ts Files", "value": f"{hls_ts_file_count}", "inline": True},
                        {"name": "Passes", "value": f"{pass_count}", "inline": True},
                        {"name": "Fails", "value": f"{fail_count}", "inline": True}
                    ],
                    "footer": {"text": "Monitoring Bot"}
                }
            ]
        }

        response = requests.post(DISCORD_WEBHOOK_URL, json=embed)
        logger.info(f"Response from Discord: {response.status_code} {response.text}")
        print(f"Response from Discord: {response.status_code} {response.text}")  # Console output

    except Exception as e:
        logger.error(f"Error sending status update to Discord: {e}")
        print(f"Error sending status update to Discord: {e}")

