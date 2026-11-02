# Alma Patron Purge Utility

This utility automates the deletion of expired patron records from the Alma library system. It reads user IDs (UIDs) from a daily/weekly generated CSV file, processes the deletions via the Alma REST API, and emails a formatted report to the system administrator.

## Components

* **`purgefromlist.py`**: The core Python script that handles the CSV parsing, Alma API communication, and report generation.

* **`patronpurgewrapper.sh`**: A Bash wrapper script designed to be run manually or via a cron job. It sets environment variables, executes the Python script, and emails the resulting report.

## Prerequisites

* **Python 3.x**

* **Python Packages**:

  * `requests`

  * `python-dotenv`

* **Linux Utilities**: `mail` (for sending the email report).

Install the required Python packages using pip:

```bash
pip install requests python-dotenv
```

## Directory Structure

The scripts expect a defined directory structure, which you will configure in the wrapper script. A standard layout looks like this:

* **Scripts directory**: `/path/to/scripts/`

* **Log directory**: `/path/to/logs/`

* **CSV Batch File**: `/path/to/batch/ExpiredPatronUID365Day.csv`

## Configuration

### 1. Environment Variables (`.env`)

The Python script requires an environment file to securely load your Alma API keys. Create a `.env` file in the same directory as `purgefromlist.py` (e.g., `/path/to/scripts/.env`) with the following content:

```ini
PRODUCTION_API_KEY=your_production_api_key_here
SANDBOX_API_KEY=your_sandbox_api_key_here
```

### 2. Testing vs. Production

By default, the script is configured for Production. If you wish to test against the Alma Sandbox environment, edit `purgefromlist.py` and change the boolean flag:

```python
use_sandbox = True  # Set to False to use the production API key
```

### 3. The Input CSV

The script expects a CSV file where:

* The first row is a header (which the script skips).

* The first column contains the primary identifiers (UIDs) of the patrons to be deleted.

## Report Levels

The script generates reports tailored for email readability, leaving the highly technical data in a local log file (`delete_users.log`). You can control the detail level of the emailed report by setting the `REPORT_LEVEL` variable in `patronpurgewrapper.sh`.

Available levels:

* **`SUMMARY`**: Provides strictly the counts of users deleted, users not deleted, and total processed. Best for quiet, successful daily runs.

* **`INFO`**: Includes the summary counts, plus a list of specific UIDs that failed to delete, along with their Alma error codes (e.g., "User has loans").

* **`DEBUG`**: Includes the summary, the info list, and full HTTP request/response traces for every processed patron.

## Usage

To run the utility, first ensure the bash wrapper is executable, then run it:

```bash
chmod +x /path/to/scripts/patronpurgewrapper.sh
/path/to/scripts/patronpurgewrapper.sh
```

### Automating with Cron

To run this script automatically (e.g., every morning at 2:00 AM), add the following to your crontab, updating the path to match your environment:

```bash
0 2 * * * /path/to/scripts/patronpurgewrapper.sh
```