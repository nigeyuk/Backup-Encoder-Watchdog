# checks.py

import requests
import xml.etree.ElementTree as ET
import subprocess
from pathlib import Path
import time
import logging
from config import (
    ICECAST_URL, ICECAST_USER, ICECAST_PASS,
    CPU_LOAD_THRESHOLD, HLS_DIRECTORY, OLD_FILE_THRESHOLD,
    MAX_TS_FILES, EXCLUDE_FILES
)
from database import log_to_database

logger = logging.getLogger(__name__)

# Global variables to track counts and PID
sources_zero_count = 0
cpu_low_count = 0
hls_old_file_count = 0
hls_ts_file_count = 0
ts_file_count_failures = 0
liquidsoap_pid = None

def get_liquidsoap_pid():
    """Retrieve the PID of the liquidsoap process."""
    try:
        result = subprocess.run(['pidof', 'liquidsoap'], capture_output=True, text=True)
        pid = result.stdout.strip()
        if pid:
            logger.info(f"Liquidsoap PID: {pid}")
            return pid
        else:
            logger.warning("Liquidsoap process not found.")
            return None
    except Exception as e:
        logger.error(f"Error getting Liquidsoap PID: {e}")
        return None

def check_icecast_sources():
    """Check if there are active sources connected to the Icecast server."""
    global sources_zero_count
    try:
        response = requests.get(
            ICECAST_URL + '/admin/stats',
            auth=(ICECAST_USER, ICECAST_PASS)
        )
        response.raise_for_status()

        root = ET.fromstring(response.content)
        sources = root.findall(".//source")
        if not sources:
            logger.warning("Sources are null or empty.")
            print("Sources are null or empty.")  # Console output
            sources_zero_count += 1
            log_to_database("Icecast Sources", "fail")
            return "fail"
        else:
            logger.info(f"Number of sources: {len(sources)}")
            print(f"Number of sources: {len(sources)}")  # Console output
            sources_zero_count = 0
            log_to_database("Icecast Sources", "pass")
            return "pass"

    except requests.RequestException as e:
        from notifications import notify_discord
        logger.error(f"Error checking Icecast status: {e}")
        print(f"Error checking Icecast status: {e}")  # Console output
        notify_discord(f"Error checking Icecast status: {e}")
        log_to_database("Icecast Sources", "fail")
        return "fail"
    except ET.ParseError as pe:
        from notifications import notify_discord
        logger.error(f"XML parsing error: {pe}")
        print(f"XML parsing error: {pe}")  # Console output
        notify_discord(f"XML parsing error: {pe}")
        log_to_database("Icecast Sources", "fail")
        return "fail"

def check_liquidsoap_cpu():
    """Check the CPU usage of the liquidsoap process using its PID."""
    global cpu_low_count, liquidsoap_pid
    try:
        pid = get_liquidsoap_pid()
        liquidsoap_pid = pid  # Update the global variable
        if pid:
            result = subprocess.run(['ps', '-p', pid, '-o', '%cpu='], capture_output=True, text=True)
            cpu_usage_value = float(result.stdout.strip())
            logger.info(f"Liquidsoap CPU usage: {cpu_usage_value}% (PID: {pid})")
            print(f"Liquidsoap CPU usage: {cpu_usage_value}% (PID: {pid})")  # Console output

            if cpu_usage_value < CPU_LOAD_THRESHOLD:
                cpu_low_count += 1
                logger.warning(f"Liquidsoap CPU usage is below {CPU_LOAD_THRESHOLD}%. Count: {cpu_low_count}")
                print(f"Liquidsoap CPU usage is below {CPU_LOAD_THRESHOLD}%. Count: {cpu_low_count}")  # Console output
                if cpu_low_count >= 3:
                    log_to_database("Liquidsoap CPU", "fail")
                    return "fail"
                else:
                    # Considered a pass until count reaches 3
                    log_to_database("Liquidsoap CPU", "pass")
                    return "pass"
            else:
                cpu_low_count = 0
                log_to_database("Liquidsoap CPU", "pass")
                return "pass"
        else:
            # Handle the case where Liquidsoap is not running
            from notifications import notify_discord
            logger.warning("Liquidsoap process is not running.")
            print("Liquidsoap process is not running.")  # Console output
            cpu_low_count += 1
            liquidsoap_pid = None  # No PID available
            notify_discord("Liquidsoap process is not running.")
            log_to_database("Liquidsoap CPU", "fail")
            return "fail"
    except Exception as e:
        from notifications import notify_discord
        logger.error(f"Error checking Liquidsoap CPU: {e}")
        print(f"Error checking Liquidsoap CPU: {e}")  # Console output
        notify_discord(f"Error checking Liquidsoap CPU: {e}")
        log_to_database("Liquidsoap CPU", "fail")
        return "fail"

def check_ts_file_count():
    """Check if the number of .ts files exceeds the maximum allowed."""
    global ts_file_count_failures, hls_ts_file_count
    try:
        ts_files = list(Path(HLS_DIRECTORY).glob('*.ts'))

        hls_ts_file_count = len(ts_files)

        if hls_ts_file_count > MAX_TS_FILES:
            logger.warning(f"Number of .ts files ({hls_ts_file_count}) exceeds the maximum allowed ({MAX_TS_FILES}).")
            print(f"Number of .ts files ({hls_ts_file_count}) exceeds the maximum allowed ({MAX_TS_FILES}).")  # Console output
            ts_file_count_failures += 1
            log_to_database("TS File Count", "fail")
            return "fail"
        else:
            ts_file_count_failures = 0
            logger.info(f"Number of .ts files ({hls_ts_file_count}) is within the acceptable range.")
            print(f"Number of .ts files ({hls_ts_file_count}) is within the acceptable range.")  # Console output
            log_to_database("TS File Count", "pass")
            return "pass"
    except Exception as e:
        from notifications import notify_discord
        logger.error(f"Error checking number of .ts files: {e}")
        print(f"Error checking number of .ts files: {e}")  # Console output
        notify_discord(f"Error checking number of .ts files: {e}")
        log_to_database("TS File Count", "fail")
        return "fail"

def check_hls_directory():
    """Check for old .ts files in the HLS directory."""
    global hls_old_file_count
    try:
        now = time.time()
        old_files = 0
        ts_files = list(Path(HLS_DIRECTORY).glob('*.ts'))

        for file in ts_files:
            if file.name in EXCLUDE_FILES:
                logger.info(f"Skipping excluded file: {file.name}")
                print(f"Skipping excluded file: {file.name}")  # Console output
                continue

            if now - file.stat().st_mtime > OLD_FILE_THRESHOLD:
                logger.warning(f"Old file found: {file.name}, last modified {time.ctime(file.stat().st_mtime)}")
                print(f"Old file found: {file.name}, last modified {time.ctime(file.stat().st_mtime)}")  # Console output
                old_files += 1

        if old_files > 0:
            hls_old_file_count += 1
            logger.warning(f"{old_files} old .ts file(s) found in HLS directory. Count: {hls_old_file_count}")
            print(f"{old_files} old .ts file(s) found in HLS directory. Count: {hls_old_file_count}")  # Console output
            log_to_database("HLS Old Files", "fail")
            return "fail"
        else:
            hls_old_file_count = 0
            logger.info("No old .ts files found in HLS directory.")
            print("No old .ts files found in HLS directory.")  # Console output
            log_to_database("HLS Old Files", "pass")
            return "pass"
    except Exception as e:
        from notifications import notify_discord
        logger.error(f"Error checking HLS directory: {e}")
        print(f"Error checking HLS directory: {e}")  # Console output
        notify_discord(f"Error checking HLS directory: {e}")
        log_to_database("HLS Old Files", "fail")
        return "fail"

