import requests
import gspread
import json
import os
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# 구글 시트 인증
def authorize_google_sheets():
    json_str = os.environ.get("GOOGLE_SHEET_JSON")
    if not json_str:
        raise ValueError("환경변수 GOOGLE_SHEET_JSON이 설정되지 않았습니다.")

    info = json.loads(json_str)
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    gc = gspread.authorize(credentials)
    return gc

# 시트에서 저장된 회차 확인
def get_saved_rounds(worksheet):
    rounds = worksheet.col_values(1)[1:]
    return set(rounds)

# 회차 데이터 요청 (예외 처리 추가)
def fetch_recent_results():
    url = "https://ntry.com/data/json/games/power_ladder/list.json"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("list", [])[:5]
    except Exception as e:
        print("⚠️ 회차 데이터 불러오기 실패:", e)
        return []

# 새 회차 저장
def save_new_rounds(worksheet, recent_data, saved_rounds):
    new_count = 0
    for item in reversed(recent_data):
        round_number = str(item["round"])
        if round_number in saved_rounds:
            continue

        created_at = item["created_at"]
        result = item["result"].replace(",", "-")
        worksheet.append_row([round_number, created_at, result])
        new_count += 1
        print(f"✅ 저장 완료: {round_number}회차")
    if new_count == 0:
        print("ℹ️ 저장할 새 회차 없음")

# 실행
def main():
    print("🟢 자동 저장 시작")
    gc = authorize_google_sheets()
    sh = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
    worksheet = sh.worksheet("예측결과")

    saved_rounds = get_saved_rounds(worksheet)
    recent_data = fetch_recent_results()
    save_new_rounds(worksheet, recent_data, saved_rounds)

if __name__ == "__main__":
    main()
