import requests
from datetime import datetime, timedelta
import os

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

KEYWORDS = [
    "malicious",
    "typosquat",
    "dependency confusion",
    "backdoor",
    "credential",
    "token",
    "exfiltrate"
]


def send_to_slack(text):
    if not SLACK_WEBHOOK_URL:
        print("❌ Missing Slack webhook")
        return

    requests.post(SLACK_WEBHOOK_URL, json={"text": text})


def fetch_osv_vulns():
    url = "https://api.osv.dev/v1/query"

    since = (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z"

    payload = {
        "query": {
            "modified_since": since
        }
    }

    response = requests.post(url, json=payload)
    data = response.json()

    return data.get("vulns", [])


def is_relevant(v):
    vuln_id = v.get("id", "").lower()
    summary = v.get("summary", "").lower()

    if vuln_id.startswith("mal"):
        return True

    return any(k in summary for k in KEYWORDS)


def main():
    print("🚀 Running supply chain scan...")

    vulns = fetch_osv_vulns()

    alerts = 0

    for v in vulns:
        if not is_relevant(v):
            continue

        affected = v.get("affected", [])
        if not affected:
            continue

        pkg = affected[0].get("package", {})
        name = pkg.get("name", "unknown")
        ecosystem = pkg.get("ecosystem", "unknown")

        message = f"""
🚨 SUPPLY CHAIN ALERT

📦 Package: {name}
🧬 Ecosystem: {ecosystem}
🆔 ID: {v.get("id")}

📝 {v.get("summary")}
"""

        send_to_slack(message)
        alerts += 1

    if alerts == 0:
        print("✅ No relevant supply chain threats")


if __name__ == "__main__":
    main()
