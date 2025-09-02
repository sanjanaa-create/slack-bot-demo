# Slack Bot

This is a simple Slack Bot that automates tasks and responds to messages in a Slack workspace. It is built using Python and the Slack Bolt SDK.

## Features

* Responds to user commands and messages
* Sends automated replies in Slack channels
* Supports slash commands
* Easy to customize and extend

## Tech Stack

* Python 3
* Slack Bolt for Python
* Slack API

## Installation

1. Clone the repository: `https://github.com/sanjanaa-create/slack-bot-demo` then `cd slack-bot`
2. (Optional) Create a virtual environment: `python -m venv venv`; activate with `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`

## Setup

1. Create a new Slack app from the Slack API dashboard
2. Add bot token scopes like `chat:write`, `app_mentions:read`, `commands`
3. Install the app to your workspace and copy the Bot User OAuth Token
4. Create a `.env` file in the project root with: `SLACK_BOT_TOKEN=xoxb-your-token-here` and `SLACK_SIGNING_SECRET=your-signing-secret-here`

## Run the Bot

Run: `python app.py`

## Contributing

Contributions are welcome. Open an issue to discuss changes before making a pull request.
