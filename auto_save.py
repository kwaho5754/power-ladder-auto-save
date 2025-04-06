import os
import json
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# 환경변수에서 구글 시트 JSON 키 가져오기
json_data = json.loads(os.environ["GOOGLE_SHEET_JSON"])

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)
gc = gspread.authorize(credentials)

# 구글 시트 열기
spreadsheet = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = spreadsheet.worksheet("예측결과")

# 실시간 회차 결과 주소
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

def fetch_latest_result():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            return data[0]  # 가장 최근 회차 1개만 추출
        else:
            print("⚠️ JSON 응답이 비어있거나 형식이 다름:", data)
            return None
    except Exception as e:
        print("❌ 회차 데이터 불러오기 실패:", e)
        return None

def get_last_round_from_sheet():
    try:
        records = worksheet.get_all_values()
        if len(records) < 2:
            return None
        last_row = records[-1]
        return int(last_row[1])  # 회차 (두 번째 열)
    except Exception as e:
        print("❌ 시트 회차 조회 실패:", e)
        return None

def save_to_sheet(data):
    try:
        reg_date = data["reg_date"]
        date_round = data["date_round"]
        start_point = data["start_point"]
        line_count = data["line_count"]
        odd_even = data["odd_even"]

        row = [reg_date, date_round, start_point, line_count, odd_even]
        worksheet.append_row(row)
        print("✅ 저장 완료:", row)
    except Exception as e:
        print("❌ 시트 저장 실패:", e)

def main():
    print("⏰ 자동 저장 시작")

    latest_data = fetch_latest_result()
    if not latest_data:
        print("⚠️ 유효한 데이터 없음. 저장 중단.")
        return

    current_round = int(latest_data.get("date_round", 0))
    last_saved_round = get_last_round_from_sheet()

    print("📝 가장 마지막 저장된 회차:", last_saved_round)
    print("🆕 지금 가져온 회차:", current_round)

    if current_round != last_saved_round:
        save_to_sheet(latest_data)
    else:
        print("🔁 이미 저장된 회차입니다. 저장 생략.")

if __name__ == "__main__":
    main()
