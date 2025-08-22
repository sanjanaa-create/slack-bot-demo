# oauth_server.py

from flask import Flask, request, redirect
import requests
from dotenv import load_dotenv
import os

# 🔹 Load variables from .env
load_dotenv()

# 🔹 Get Slack credentials from environment
CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SLACK_OAUTH_REDIRECT")
SCOPES = os.getenv("SLACK_SCOPES", "app_mentions:read,chat:write")

# 🔹 Check if essential credentials are missing
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    raise ValueError(
        "⚠️ Missing Slack credentials! "
        "Please check your .env file for CLIENT_ID, CLIENT_SECRET, and REDIRECT_URI"
    )

app = Flask(__name__)

@app.route("/slack/install")
def install():
    """Redirects user to Slack OAuth permission page"""
    oauth_url = (
        "https://slack.com/oauth/v2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}"
    )
    return redirect(oauth_url)

@app.route("/slack/oauth_redirect")
def oauth_redirect():
    """Handles Slack OAuth redirect and exchanges code for access token"""
    code = request.args.get("code")
    if not code:
        return "❌ Missing 'code' parameter in redirect."

    try:
        resp = requests.post(
            "https://slack.com/api/oauth.v2.access",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            timeout=10
        ).json()
    except requests.RequestException as e:
        return f"❌ Network error: {e}"

    if resp.get("ok"):
        access_token = resp.get("access_token")
        team_name = resp.get("team", {}).get("name", "Unknown Team")
        return f"✅ App installed successfully on '{team_name}'!\nAccess token: {access_token}"
    else:
        error = resp.get("error", "Unknown error")
        return f"❌ Slack API Error: {error}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
