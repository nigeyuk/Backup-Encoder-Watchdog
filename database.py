# database.py

import mysql.connector
from mysql.connector import Error
from config import ENABLE_DB_LOGGING, DB_HOST, DB_USER, DB_PASS, DB_NAME
import logging

logger = logging.getLogger(__name__)

def log_to_database(flag_name, status):
    if not ENABLE_DB_LOGGING:
        return  # Skip logging if disabled

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        if connection.is_connected():
            cursor = connection.cursor()
            sql = "INSERT INTO monitoring_logs (timestamp, flag_name, status) VALUES (NOW(), %s, %s)"
            cursor.execute(sql, (flag_name, status))
            connection.commit()
            cursor.close()
            logger.info(f"Logged to database: {flag_name} - {status}")
            print(f"Logged to database: {flag_name} - {status}")  # Console output
    except Error as e:
        logger.error(f"Error logging to database: {e}")
        print(f"Error logging to database: {e}")  # Console output
        from notifications import notify_discord
        notify_discord(f"Error logging to database: {e}")
    finally:
        if connection.is_connected():
            connection.close()
