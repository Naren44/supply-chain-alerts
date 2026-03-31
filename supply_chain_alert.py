import requests
from datetime import datetime, timedelta
import os

# 🔐 Slack webhook (set in GitHub Secrets)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# 🔍 supply chain keywords
KEYWORDS = [
    "malicious",
    "typosquat",
    "dependency confusion",
    "backdoor",
    "credential",
    "token",
    "exfiltrate",
    "obfuscat"
]

TARGET_ECOSYSTEMS = ["npm", "pypi"]


def send_to_slack(text):
    if not SLACK_WEBHOOK_URL:
        print("❌ Missing SLACK_WEBHOOK_URL")
        return

    requests.post(SLACK_WEBHOOK_URL, json={"text": text})


def fetch_recent_vulns():
    url = "https://api.osv.dev/v1/query"

    # ⏱️ last 12 hours
    since = (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z"

    payload = {
        "query": {
            "modified_since": since
        }
    }

    response = requests.post(url, json=payload)

    print("🌐 API Status:", response.status_code)

    data = response.json()
    vulns = data.get("vulns", [])

    print(f"📊 Fetched {len(vulns)} vulnerabilities")

    return vulns


def is_relevant(v):
    vuln_id = v.get("id", "").lower()
    summary = v.get("summary", "").lower()

    # 🚨 malicious advisories
    if vuln_id.startswith("mal"):
        return True

    # 🔍 keyword detection
    if any(k in summary for k in KEYWORDS):
        return True

    return False


def process_vulns():
    vulns = fetch_recent_vulns()

    alerts = 0

    for v in vulns:
        vuln_id = v.get("id", "N/A")

        affected = v.get("affected", [])
        if not affected:
            continue

        package = affected[0].get("package", {})
        ecosystem = package.get("ecosystem", "").lower()
        name = package.get("name", "unknown")

        # 🎯 filter ecosystem
        if ecosystem not in TARGET_ECOSYSTEMS:
            continue

        # 🧠 filter supply chain patterns
        if not is_relevant(v):
            continue

        summary = v.get("summary", "No summary")

        message = f"""
🚨 SUPPLY CHAIN ALERT

🆔 {vuln_id}
📦 {name}
🧬 {ecosystem}

📝 {summary}
"""

        send_to_slack(message)
        alerts += 1

    if alerts == 0:
        print("✅ No relevant supply chain alerts found")


if __name__ == "__main__":
    process_vulns()