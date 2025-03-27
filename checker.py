import datetime
import os

import requests
from bs4 import BeautifulSoup

URL = os.getenv('RAKUTEN_URL')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')

def send_email(subject, content):
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    data = {
        "sender": {"email": SENDER_EMAIL},
        "to": [{"email": RECIPIENT_EMAIL}],
        "subject": subject,
        "htmlContent": content
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 201:
        print("Email sending failed:", response.status_code, response.text)
    else:
        print("Email sent successfully.")

if __name__ == "__main__":
    # 強制的にメールを送る（デバッグのため）
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = "【デバッグテスト】強制的なメール送信テスト"
    content = f"<p>{now} にデバッグのため強制送信されたメールです。</p><a href='{URL}'>リンク</a>"
    send_email(subject, content)