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

    r = requests.post(SLACK_WEBHOOK_URL, json={"text": text})
    print("Slack status:", r.status_code)


def main():
    try:
        print("🚀 Script started")

        url = "https://api.osv.dev/v1/query"
        since = (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z"

        payload = {
            "query": {
                "modified_since": since
            }
        }

        print("📡 Calling OSV API...")
        response = requests.post(url, json=payload)

        print("Status Code:", response.status_code)
        print("Raw Response:", response.text[:500])  # print partial response

        data = response.json()

        vulns = data.get("vulns", [])
        print(f"📊 Found {len(vulns)} vulnerabilities")

        if not vulns:
            print("✅ No vulnerabilities found")
            return

        first = vulns[0]
        summary = first.get("summary", "No summary")

        send_to_slack(f"🚨 Test Alert:\n{summary}")

    except Exception as e:
        print("🔥 ERROR OCCURRED:")
        print(str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
