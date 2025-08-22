import os
import re
from collections import defaultdict, deque

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI

# -----------------------
# Load environment variables
# -----------------------
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
BOT_MODE = os.getenv("BOT_MODE", "dummy")  # "dummy" or "openai"

# Validate tokens
if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
    raise RuntimeError("❌ Missing Slack tokens. Check .env file.")

print(f"✅ Tokens loaded. Running in {BOT_MODE.upper()} mode.")

# -----------------------
# Initialize Slack app
# -----------------------
app = App(token=SLACK_BOT_TOKEN)

# Initialize OpenAI only if needed
client_llm = None
if BOT_MODE == "openai":
    if not OPENAI_API_KEY:
        raise RuntimeError("❌ BOT_MODE=openai but no OpenAI API key found.")
    client_llm = OpenAI(api_key=OPENAI_API_KEY)

# Memory: store last 10 messages (5 user+bot pairs) per conversation
memory = defaultdict(lambda: deque(maxlen=10))

SYSTEM_PROMPT = (
    "You are Warpi, a helpful Slack bot. "
    "Answer clearly and use past context when relevant."
)

# -----------------------
# Helper functions
# -----------------------
def build_llm_messages(history, user_text):
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    msgs.extend(list(history))
    msgs.append({"role": "user", "content": user_text})
    return msgs

def generate_reply(history, user_text):
    if BOT_MODE == "openai":
        print("🤖 Using OpenAI for reply:", user_text)
        try:
            resp = client_llm.chat.completions.create(
                model=OPENAI_MODEL,
                messages=build_llm_messages(history, user_text),
                temperature=0.4,
            )
            reply = resp.choices[0].message.content.strip()
            print("✅ OpenAI replied with:", reply)
            return reply
        except Exception as e:
            print("❌ OpenAI Error:", e)
            return f"Error: {e}"
    else:
        print("🤖 Dummy reply triggered:", user_text)
        return f"You said: {user_text}"

def convo_key(event):
    return event.get("channel") if event.get("channel_type") != "im" else event.get("user")

def handle_text(event, say):
    print("📩 Handling event:", event)  # Debug

    if event.get("subtype") in {"bot_message", "message_changed", "message_deleted"}:
        print("⚠️ Ignored subtype event:", event.get("subtype"))
        return

    text = event.get("text", "").strip()
    if not text:
        print("⚠️ No text found in event")
        return

    # Remove bot mention if present
    bot_user_id = app.client.auth_test()["user_id"]
    mention_pattern = fr"<@{bot_user_id}>\s*"
    user_text = re.sub(mention_pattern, "", text).strip()

    print(f"👤 User text: {user_text}")

    # Store history
    key = convo_key(event)
    memory[key].append({"role": "user", "content": user_text})

    # Generate reply
    reply = generate_reply(memory[key], user_text)

    # Send reply
    try:
        say(text=reply)
        print("✅ Sent reply to Slack.")
    except Exception as e:
        print("❌ Slack send error:", e)

    memory[key].append({"role": "assistant", "content": reply})

# -----------------------
# Event Listeners
# -----------------------
@app.event("app_mention")
def on_mention(body, event, say, logger):
    print("📩 App mention event received:", event)
    handle_text(event, say)

@app.event("message")
def on_message(body, event, say, logger):
    print("📩 Message event received:", event)
    if event.get("channel_type") == "im" and not event.get("bot_id"):
        handle_text(event, say)

# -----------------------
# Main entry
# -----------------------
if __name__ == "__main__":
    print("✅ Warpi bot running... (Ctrl+C to stop)")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
