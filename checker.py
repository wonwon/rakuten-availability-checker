import datetime
import json
import os
from datetime import timedelta

import requests

APP_ID = os.getenv("RAKUTEN_APP_ID")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

HOTEL_NO = "136902"
ADULT_NUM = 1
HOTEL_URL = f"https://hotel.travel.rakuten.co.jp/hinfo/{HOTEL_NO}/"

API_URL = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"

# ✅ 監視対象：5月のみ（今日から残り日程を確認）
start_date = datetime.date(2025, 5, 1)
end_date = datetime.date(2025, 5, 31)


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
        print("❌ メール送信失敗:", response.status_code, response.text)
    else:
        print("📧 メール送信成功")

# 5月1日〜5月30日まで、1泊でループ
current_date = start_date
while current_date < end_date:
    checkin = current_date.strftime("%Y-%m-%d")
    checkout = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")

    params = {
        "applicationId": APP_ID,
        "hotelNo": HOTEL_NO,
        "checkinDate": checkin,
        "checkoutDate": checkout,
        "adultNum": ADULT_NUM,
        "format": "json"
    }

    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        hotels = data.get("hotels", [])

        if hotels:
            print(f"✅ {checkin} 宿泊可能なプランが見つかりました！")
            for hotel in hotels:
                try:
                    hotel_info = hotel["hotel"][0]["hotelBasicInfo"]
                    room_info = hotel["hotel"][1]["roomInfo"][0]["roomBasicInfo"]
                    daily_charge = hotel["hotel"][1]["roomInfo"][1]["dailyCharge"]["total"]

                    print(f"🏨 {hotel_info['hotelName']} / 🛏 {room_info['planName']} / 💰 {daily_charge}円")

                    subject = f"【楽天】{checkin} 宿泊可能プランあり！"
                    content = f"""
                        <p>{checkin} に宿泊可能なプランが見つかりました。</p>
                        <ul>
                          <li>🏨 ホテル名: {hotel_info['hotelName']}</li>
                          <li>🛏 プラン: {room_info['planName']}</li>
                          <li>💰 料金: {daily_charge}円</li>
                          <li>📍 アクセス: {hotel_info['access']}</li>
                        </ul>
                        <p><a href='{HOTEL_URL}'>▶ ご予約ページへ</a></p>
                    """
                    send_email(subject, content)
                except Exception as e:
                    print(f"⚠️ 情報取得エラー: {e}")
        else:
            print(f"❌ {checkin} は空室なし")
    else:
        print(f"❌ APIエラー（{checkin}）: {response.status_code}")

    current_date += timedelta(days=1)
