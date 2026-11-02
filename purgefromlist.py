#!/usr/bin/env python3
# Deletes Patrons referenced in a batch CSV file.
import os
import csv
import sys
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# File paths & Configuration (use environment variables or defaults)
batch_file = os.environ.get("batch_file", "/path/to/your/batch/file/ExpiredPatronUID365Day.csv")
log_file = os.environ.get("LOG_FILE", "/path/to/your/log/directory/delete_users.log")
report_file = os.environ.get("REPORT_FILE", "/path/to/your/log/directory/purge_report.txt")

# Report level switch: 'SUMMARY', 'INFO', or 'DEBUG' (defaults to INFO)
report_level = os.environ.get("REPORT_LEVEL", "INFO").upper()
if len(sys.argv) > 1 and sys.argv[1].upper() in ["SUMMARY", "INFO", "DEBUG"]:
    report_level = sys.argv[1].upper()

# API Keys & Environment Selection
# Make sure PRODUCTION_API_KEY and SANDBOX_API_KEY are defined in your .env file
production_apikey = os.getenv('PRODUCTION_API_KEY')
sandbox_apikey = os.getenv('SANDBOX_API_KEY')

# Set to True for sandbox testing, False for production
use_sandbox = True
apikey = sandbox_apikey if use_sandbox else production_apikey

# Setup system file logging (keeps all details on disk)
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Tracking structures
deleted_users = []
failed_users = []  # list of dicts: {'uid': uid, 'status': code, 'reason': msg, 'debug_info': dict}
debug_traces = []

# Define the API URL template
# Adjust user_id_type as needed (e.g., all_unique, 90 for  OtherID, 99 for FileId, 01 for barcode)
url_template = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/{uid}?user_id_type=90&apikey={apikey}"

def delete_user(uid, apikey):
    url = url_template.format(uid=uid, apikey=apikey)
    headers = {"Accept": "application/json"}
    
    try:
        response = requests.delete(url, headers=headers, timeout=30)
        
        debug_entry = {
            "uid": uid,
            "url": url_template.format(uid=uid, apikey="[REDACTED]"),
            "status_code": response.status_code,
            "response_body": response.text.strip()
        }
        debug_traces.append(debug_entry)
        
        logging.debug(f"Request: {debug_entry['url']} | Response: {response.status_code} - {response.text}")
        
        if response.status_code == 204:
            logging.info(f"UID: {uid} deleted successfully (Status 204).")
            deleted_users.append(uid)
        else:
            logging.warning(f"UID: {uid} not deleted. Status: {response.status_code}, Response: {response.text}")
            failed_users.append({
                "uid": uid,
                "status": response.status_code,
                "reason": response.text.strip(),
                "debug": debug_entry
            })
    except Exception as e:
        logging.error(f"Exception deleting UID {uid}: {e}")
        failed_users.append({
            "uid": uid,
            "status": "ERROR",
            "reason": str(e),
            "debug": {"uid": uid, "exception": str(e)}
        })

# Read UIDs
uids = []
try:
    with open(batch_file, newline='') as csvfile:
        uid_reader = csv.reader(csvfile)
        next(uid_reader, None)  # Skip header
        uids = [row[0].strip() for row in uid_reader if row and row[0].strip()]
    logging.info(f"Loaded {len(uids)} UIDs from {batch_file}")
except Exception as e:
    logging.error(f"Failed to read CSV file: {e}")
    failed_users.append({"uid": "N/A", "status": "FILE_ERROR", "reason": f"Could not read {batch_file}: {e}", "debug": {}})

# Process batch
for uid in uids:
    delete_user(uid, apikey)

# Build formatted email report
report_lines = []

# ==================== SUMMARY SECTION ====================
report_lines.append("=" * 45)
report_lines.append("              PURGE SUMMARY")
report_lines.append("=" * 45)
report_lines.append(f"Users Deleted:     {len(deleted_users)}")
report_lines.append(f"Users Not Deleted: {len(failed_users)}")
report_lines.append(f"Total Processed:   {len(uids)}")
report_lines.append("=" * 45)

# ==================== INFO SECTION ====================
if report_level in ["INFO", "DEBUG"]:
    report_lines.append("\n" + "-" * 45)
    report_lines.append("                   INFO")
    report_lines.append("-" * 45)
    
    if failed_users:
        report_lines.append("Users Not Deleted:")
        for item in failed_users:
            report_lines.append(f"  - UID: {item['uid']:<15} Status: {item['status']:<6} Reason: {item['reason'][:80]}")
    else:
        report_lines.append("All patrons in this batch were successfully deleted.")

# ==================== DEBUG SECTION ====================
if report_level == "DEBUG":
    report_lines.append("\n" + "-" * 45)
    report_lines.append("                  DEBUG")
    report_lines.append("-" * 45)
    report_lines.append(f"Batch Source File: {batch_file}")
    report_lines.append(f"Target Environment: {'Sandbox' if use_sandbox else 'Production'}")
    report_lines.append("\nDetailed API Traces:")
    for trace in debug_traces:
        report_lines.append(f"  UID: {trace['uid']}")
        report_lines.append(f"    URL:    {trace['url']}")
        report_lines.append(f"    Status: {trace['status_code']}")
        report_lines.append(f"    Body:   {trace['response_body']}")
        report_lines.append("")

# Write output report for email
with open(report_file, "w") as f:
    f.write("\n".join(report_lines) + "\n")

print(f"Report written to {report_file} (Level: {report_level}). Log file: {log_file}")