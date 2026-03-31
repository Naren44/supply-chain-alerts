import requests
from datetime import datetime, timedelta
import os
import sys

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_to_slack(text):
    print("➡️ Sending to Slack...")

    if not SLACK_WEBHOOK_URL:
        print("❌ SLACK_WEBHOOK_URL is missing")
        sys.exit(1)

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json={"text": text}
        )

        print("Slack Status Code:", response.status_code)
        print("Slack Response:", response.text)

    except Exception as e:
        print("❌ Slack error:", str(e))


def fetch_osv_vulns():
    url = "https://api.osv.dev/v1/query"

    since = (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z"

    payload = {
        "query": {
            "modified_since": since
        }
    }

    print("📡 Calling OSV API...")

    response = requests.post(url, json=payload)

    print("OSV Status:", response.status_code)

    data = response.json()
    vulns = data.get("vulns", [])

    print(f"📊 Found {len(vulns)} vulnerabilities")

    return vulns


def main():
    print("🚀 Script started")

    # 🔥 Step 1: Always send test message
    send_to_slack("🔥 TEST: Slack integration is working!")

    # 🔍 Step 2: Fetch OSV data
    vulns = fetch_osv_vulns()

    if not vulns:
        print("✅ No vulnerabilities found")
        return

    # 🚨 Step 3: Send first vulnerability (demo)
    first = vulns[0]
    vuln_id = first.get("id", "N/A")
    summary = first.get("summary", "No summary")

    message = f"""
🚨 SUPPLY CHAIN ALERT

ID: {vuln_id}
Summary: {summary}
"""

    send_to_slack(message)


if __name__ == "__main__":
    main()
