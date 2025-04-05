import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

print("🔵 자동 저장 시작")

# URL
URL = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

def fetch_latest_result():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(URL, headers=headers)
        response.raise_for_status()  # HTTP 에러 시 예외 발생
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("❗ 회차 데이터 불러오기 실패:", e)
        return None
    except json.decoder.JSONDecodeError as e:
        print("❗ JSON 디코드 실패:", e)
        return None

def load_credentials():
    try:
        credentials_dict = json.loads(os.environ["GOOGLE_SHEET_JSON"])
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print("❗ 구글 인증 실패:", e)
        return None

def save_to_sheet(data):
    if not data:
        print("❌ 저장할 데이터 없음")
        return

    client = load_credentials()
    if not client:
        return

    sheet = client.open("실시간결과").worksheet("예측결과")
    existing_rounds = sheet.col_values(2)  # B열 (date_round)
    
    latest_round = str(data["date_round"])
    if latest_round in existing_rounds:
        print("ℹ️ 저장할 새 회차 없음")
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        now,
        data["date_round"],
        data["round"],
        data["result"],
        data["start_point"],
        data["line_count"],
        data["odd_even"]
    ]
    sheet.append_row(row)
    print("✅ 시트 저장 완료:", row)

def main():
    latest_result = fetch_latest_result()
    save_to_sheet(latest_result)

if __name__ == "__main__":
    main()
