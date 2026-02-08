import requests
import csv
from datetime import datetime, timedelta
from collections import Counter
import os

token = os.getenv("AIRTABLE_TOKEN")
BASE_ID = "appoRz29MiPqvJ3i4"
TABLE_NAME = "Requests"

CONSULTANTS_TABLE = "Consultants"
CONSULTANTS_URL = f"https://api.airtable.com/v0/{BASE_ID}/{CONSULTANTS_TABLE}"

URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(URL, headers=HEADERS, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print("❌ Error fetching data from Airtable")
    print(e)
    exit()

records = response.json().get("records", [])

now = datetime.utcnow()
week_ago = now - timedelta(days=7)

new_requests = 0
closed_requests = 0
processing_times = []

for record in records:
    fields = record.get("fields", {})

    created = fields.get("Created At")
    closed = fields.get("Closed At")
    status = fields.get("Status")

    # ---- New requests (last 7 days)
    if created:
        try:
            created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")

        if created_dt >= week_ago:
            new_requests += 1

    # ---- Closed requests + processing time
    if status == "Closed" and created and closed:
        try:
            created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")

        try:
            closed_dt = datetime.strptime(closed, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            closed_dt = datetime.strptime(closed, "%Y-%m-%dT%H:%M:%SZ")

        processing_time_hours = (closed_dt - created_dt).total_seconds() / 3600
        processing_times.append(processing_time_hours)
        closed_requests += 1


with open("weekly_report.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["New requests (last 7 days)", new_requests])
    writer.writerow(["Closed requests", closed_requests])

    if processing_times:
        average_time = round(sum(processing_times) / len(processing_times), 2)
    else:
        average_time = 0

    writer.writerow(["Average processing time (hours)", average_time])

print("✅ weekly_report.csv successfully created")
