# Backup-Encoder-Watchdog

## Overview
 The Backup Encoder Watchdog is a Python script designed to monitor critical parameters of your primary encoder server and, in the event of a failure, automatically bring up a backup encoder server using AWS CLI. The script checks multiple metrics, including Icecast source status, Liquidsoap CPU usage, the number of HLS segments, and the freshness of ```.ts``` files in the HLS directory.

## Features
* Monitors critical parameters of the encoder server.
* Automatically starts a backup AWS encoder instance if multiple parameters fail.
* Sends detailed status updates and alerts to a Discord channel.
* Logs all activity and metrics to a MySQL database for historical tracking.
* Periodic and on-demand status updates to Discord with detailed information on the current state of each parameter.
* Configurable thresholds and behavior through an ```.env``` file.

## Prerequisites
* Python 3.6 or later
* AWS CLI configured with necessary permissions
* MySQL database for logging
* Discord webhook URL for notifications

## Setup
### 1. Clone the Repository
```
git clone https://github.com/yourusername/backup-encoder-watchdog.git
cd backup-encoder-watchdog
```
### 2. Install Required Python Packages
Create a virtual environment (optional but recommended):
```
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
Install the required packages:
```
pip install -r requirements.txt
```

### 3. Configure the .env file.
Create a ```.env``` file in the root directory and populate it with the necessary environment variables:
```.env
# .env
# IceCast Server Configuration
ICECAST_URL=http://icecast-server-url:9000 # Your IceCast Server URL
ICECAST_USER=adminusername # Your IceCast admin user
ICECAST_PASS=password # Your IceCast admin password

#HLS Directory Config
HLS_DIRECTORY=/path/to/HLS # Path to your HLS directory as set in your liquidsoap script
MAX_TS_FILES=20  # The expected number of .ts files in the HLS directory
EXCLUDE_FILES=index.html,live.m3u8 #you generally want to exclude any non .ts files
OLD_FILE_THRESHOLD=900  # Set the old file threshold (in seconds, e.g., 900 seconds = 15 minutes)

# CPU Load Config
CPU_LOAD_THRESHOLD=20.0  # Set the CPU load threshold (in percentage)

# Spin up threshhold - VERY IMPORTANT
WAIT_TIME_BEFORE_BACKUP=300  # Set the wait time before bringing up the backup encoder server (in seconds)

# Discord Config
ENABLE_DISCORD_UPDATES=True  # Set to True to enable Discord updates
DISCORD_UPDATE_INTERVAL=3600  # Duration to wait for updates (in seconds, default is 900 seconds = 15 minutes)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/

# Database Config
ENABLE_DB_LOGGING=True  # Set to True to enable MySQL logging
DB_HOST=localhost
DB_USER=username
DB_PASS=password
DB_NAME=watchdog #if you change db_name here make sure to change the db_name in the scq schema below.

# Backup instance id (this can be found in the aws console, or by using the aws cli to list instances.)
AWS_BACKUP_INSTANCE_ID= #The instance ID of your server that will be the backup encoder.
```

### 4. Set Up MySQL Database
Create the necessary tables in the MySQL database using the following schema:
```sql
CREATE DATABASE IF NOT EXISTS watchdog;
USE watchdog;

CREATE TABLE IF NOT EXISTS monitoring_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    parameter VARCHAR(50),
    status ENUM('pass', 'fail') NOT NULL
);
```

### 5. Configure AWS CLI
Ensure your AWS CLI is configured with the necessary permissions to start and stop EC2 instances.  More about the AWS CLI [Here](https://tinyurl.com/2ys84rje)
```
aws configure
```

# Usage
### 1. Running the Script
To start the watchdog script, use the following command:
```
python watchdog.py
```
# Behaviour

## Monitoring and Detection
The script monitors the following parameters:

1. **Icecast Source Status:** Checks if there are active sources connected to the Icecast server.
   
2. **Liquidsoap CPU Usage:** Monitors the CPU usage of the Liquidsoap process. 
If the usage drops below the threshold for a specified number of checks, it is flagged as a failure.

3. **HLS Directory Files:** Checks for ```.ts``` files in the HLS directory. 
If the number of files exceeds the maximum allowed or if any files are older than the defined threshold, it is flagged as a failure.

## Failover Actions
* If 2 or more parameters are in a failed state, the script will send a warning to Discord and then,
  after a configurable wait time, start the backup encoder instance.

* All actions are logged in the console, alocal log file, and the MySQL database.

# Discord Notifications
The script send the following types of notifications to Discord:

1. **Online Notification**: Sent when the script starts
   ```The monitoring bot has restarted at 2024-09-26 15:39:59 and is now actively monitoring.```

2. **Status Updates**: Sent periodically based on the configured interval.

    ![Discord Status Update](https://hls.tranceairwaves.co.uk/Discord_89MwrvTZgn.png)

3. **Error Alerts**: Sent when an error or occurs or when parameters fail.
   ```
   Error checking Icecast status: HTTPConnectionPool(host='streamer-1-eu.tranceairwaves.co.uk', port=9000):
   Max retries exceeded with url: /admin/stats (Caused by NewConnectionError('<urllib3.connection.HTTPConnection
   object at 0x7dfcc8ea9fa0>: Failed to establish a new connection: [Errno 111] Connection refused'))
   ```

# Logging

* Logs are stored in ```watchdog.log``` with daily rotation.

* All parameter statuses are logged to the MySQL database for historical tracking.

```
| 7990 | 2024-09-26 16:00:00 | Icecast Sources | pass   |
| 7991 | 2024-09-26 16:00:00 | Liquidsoap CPU  | pass   |
| 7992 | 2024-09-26 16:00:00 | TS File Count   | pass   |
| 7993 | 2024-09-26 16:00:00 | HLS Old Files   | pass   |
| 7994 | 2024-09-26 16:05:00 | Icecast Sources | pass   |
| 7995 | 2024-09-26 16:05:00 | Liquidsoap CPU  | pass   |
| 7996 | 2024-09-26 16:05:00 | TS File Count   | pass   |
| 7997 | 2024-09-26 16:05:00 | HLS Old Files   | pass   |
+------+---------------------+-----------------+--------+
7997 rows in set (0.012 sec)
```

# Troubleshooting

## Common Issues

**1. AWS CLI Not Configured**:
  * Ensure that the AWS CLI is configured with the correct permissions and that the ```AWS_BACKUP_INSTANCE_ID``` is correct in the ```.env``` file.

**2. MySQL Connections Errors:**
  * Verify that the MySQL credentials in the ```.env``` file are correct and that the database and table exist.

**3. Discord Notifications Not Sent:**
  * Check if  ```ENABLED_DISCORD_UPDATES``` is set to ```True``` in the ```.env``` file and that the Webhook URL is correct.

**While this script has been made public, it has only been tested under very specific conditions, it may not behave in the way you would like 
without some necessary changes.**

# Contributing
Feel free to submit issues or pull requests. For major changes, please open an issue to discuss your proposed changes.

License
This project is licensed under the MIT License. See the LICENSE file for details.
