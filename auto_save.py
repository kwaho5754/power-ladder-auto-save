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

# 시트에서 가장 최근 저장된 회차 확인
def get_last_saved_round(worksheet):
    rounds = worksheet.col_values(1)[1:]  # 첫 열, 헤더 제외
    return int(rounds[-1]) if rounds else 0

# 최근 회차 1개 가져오기
def fetch_latest_result():
    url = "https://ntry.com/data/json/games/power_ladder/list.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data["list"][0]  # 가장 최신 회차 1개

# 시트에 새로운 회차 추가
def save_round(worksheet, result):
    values = [
        result["date_round"],
        result["reg_date"],
        result["start_point"],
        result["line_count"],
        result["odd_even"],
    ]
    worksheet.append_row(values, value_input_option="USER_ENTERED")

# 메인 실행
def main():
    print("백그라운드 작업 실행 중...")

    gc = authorize_google_sheets()
    sh = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")  # 시트 ID
    worksheet = sh.worksheet("예측결과")  # 시트 이름

    latest_saved = get_last_saved_round(worksheet)
    print("가장 마지막 저장된 회차:", latest_saved)

    latest_result = fetch_latest_result()
    current_round = int(latest_result["date_round"])
    print("현재 회차:", current_round)

    if current_round > latest_saved:
        save_round(worksheet, latest_result)
        print("✅ 새로운 회차 저장 완료:", current_round)
    else:
        print("⚠️ 저장할 새로운 데이터가 없습니다.")

if __name__ == "__main__":
    main()
