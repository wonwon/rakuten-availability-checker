import datetime
import os

import requests
from bs4 import BeautifulSoup

# 環境変数から取得
URL = os.getenv('RAKUTEN_URL')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')

# 空室があることを示すマーク
AVAILABLE_MARK = '○'

# テスト用（5月を監視対象に設定）
TARGET_MONTHS = ['2025年5月']
# 本番用（7月〜9月）に戻す場合はこちらを使用
# TARGET_MONTHS = ['2025年7月', '2025年8月', '2025年9月']

def check_calendar_availability(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    res.encoding = 'UTF-8'

    if res.status_code != 200:
        return False, []

    soup = BeautifulSoup(res.text, 'html.parser')
    available_dates = []

    for month in TARGET_MONTHS:
        month_section = soup.find('div', string=month)
        if month_section:
            calendar = month_section.find_next('table')
            if calendar:
                days = calendar.find_all('td')
                for day in days:
                    if AVAILABLE_MARK in day.text:
                        date = day.text.strip().replace(AVAILABLE_MARK, '').strip()
                        available_dates.append(f"{month} {date}日")

    return len(available_dates) > 0, available_dates

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
    requests.post(url, json=data, headers=headers)

if __name__ == "__main__":
    has_availability, dates = check_calendar_availability(URL)
    if has_availability:
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        subject = "【楽天トラベル】宿泊可能な日程があります！（テスト）"
        content = f"<p>{now}現在、以下の日程で宿泊予約可能です（テスト用）：</p><ul>"
        for date in dates:
            content += f"<li>{date}</li>"
        content += f"</ul><p><a href='{URL}'>予約ページへ進む</a></p>"
        send_email(subject, content)