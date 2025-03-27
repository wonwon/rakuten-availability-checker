import datetime
import json
import os

import requests

# 環境変数から取得
APP_ID = os.getenv("RAKUTEN_APP_ID")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")

# 宿泊施設情報
HOTEL_NO = "136902"
CHECKIN_DATE = "2025-05-18"
CHECKOUT_DATE = "2025-05-19"
ADULT_NUM = 1
HOTEL_URL = f"https://hotel.travel.rakuten.co.jp/hinfo/{HOTEL_NO}/"

API_URL = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"

params = {
    "applicationId": APP_ID,
    "hotelNo": HOTEL_NO,
    "checkinDate": CHECKIN_DATE,
    "checkoutDate": CHECKOUT_DATE,
    "adultNum": ADULT_NUM,
    "format": "json"
}

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

response = requests.get(API_URL, params=params)

if response.status_code == 200:
    data = response.json()
    hotels = data.get("hotels", [])

    if hotels:
        print("✅ 宿泊可能なプランが見つかりました！")
        for hotel in hotels:
            try:
                hotel_info = hotel["hotel"][0]["hotelBasicInfo"]
                room_info = hotel["hotel"][1]["roomInfo"][0]["roomBasicInfo"]
                daily_charge = hotel["hotel"][1]["roomInfo"][1]["dailyCharge"]["total"]

                print(f"🏨 {hotel_info['hotelName']}")
                print(f"🛏 {room_info['planName']}")
                print(f"💰 {daily_charge}円")
                print("-" * 40)

                # メール通知内容
                now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                subject = f"【楽天】{CHECKIN_DATE} 宿泊可能なプランがあります！"
                content = f"""
                    <p>{now} に宿泊可能なプランが見つかりました。</p>
                    <ul>
                      <li>🏨 ホテル名: {hotel_info['hotelName']}</li>
                      <li>🛏 プラン: {room_info['planName']}</li>
                      <li>💰 料金: {daily_charge}円</li>
                      <li>📍 アクセス: {hotel_info['access']}</li>
                    </ul>
                    <p><a href='{HOTEL_URL}'>▶ ご予約ページへ</a></p>
                """
                send_email(subject, content)

            except (KeyError, IndexError, TypeError) as e:
                print(f"⚠️ 情報取得エラー: {e}")
    else:
        print("❌ 空室なし")
else:
    print(f"❌ APIエラー: ステータスコード {response.status_code}")
