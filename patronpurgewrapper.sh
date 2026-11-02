#!/bin/bash

# Ensure script stops on first error
set -e

# Change to the directory containing the purge script
cd /path/to/your/purge/directory

# File paths & Configuration
export batch_file="/path/to/your/batch/file/ExpiredPatronUID365Day.csv"
export log_file="/path/to/your/log/directory/delete_users.log"
export report_file="/path/to/your/log/directory/purge_report.txt"

# Select report detail level: SUMMARY, INFO, or DEBUG
export REPORT_LEVEL="SUMMARY"

# Ensure log directory exists
mkdir -p /path/to/your/log/directory

# Run the Python purge script
python3 purgefromlist.py

# Send the clean report rather than the raw log
mail -s "Expired Patron Delete Report ($REPORT_LEVEL)" "your-email@example.edu" < "$report_file"