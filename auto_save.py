import requests
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 구글 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = os.environ.get("GOOGLE_SHEET_JSON")

if not json_data:
    print("❌ 환경변수 GOOGLE_SHEET_JSON 없음")
    exit()

try:
    service_account_info = json.loads(json_data)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4").worksheet("예측결과")
except Exception as e:
    print("❗ 구글 인증 실패:", e)
    exit()

def fetch_latest_result():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("⚠️ 회차 데이터 불러오기 실패:", e)
        return None

def get_last_round_from_sheet():
    try:
        values = sheet.get_all_values()
        if len(values) < 2:
            return 0
        return int(values[-1][0])  # 첫 번째 열: 회차 번호
    except Exception as e:
        print("❌ 시트에서 마지막 회차 불러오기 실패:", e)
        return 0

def save_new_result_if_needed(new_result):
    last_round = get_last_round_from_sheet()
    new_round = int(new_result["date_round"])

    if new_round > last_round:
        row = [
            new_result["date_round"],
            new_result["start_point"],
            new_result["line_count"],
            new_result["odd_even"],
            new_result["reg_date"]
        ]
        sheet.append_row(row)
        print(f"✅ 새로운 회차 저장 완료: {new_round}")
    else:
        print("ℹ️ 저장할 새 회차 없음")

def main():
    print("✅ 자동 저장 시작")
    recent_data = fetch_latest_result()
    if recent_data:
        save_new_result_if_needed(recent_data)

if __name__ == "__main__":
    main()
