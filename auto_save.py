
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

# 시트에서 이미 저장된 회차 가져오기
def get_saved_rounds(worksheet):
    rounds = worksheet.col_values(1)[1:]  # 첫 번째 열, 헤더 제외
    return set(rounds)

# 회차 데이터 요청
def fetch_recent_results():
    url = "https://ntry.com/data/json/games/power_ladder/list.json"
    response = requests.get(url)
    data = response.json()
    return data["list"][:5]  # 최근 5개 회차

# 회차 저장
def save_new_rounds(worksheet, recent_data, saved_rounds):
    new_count = 0
    for item in reversed(recent_data):
        round_number = str(item["round"])
        if round_number in saved_rounds:
            continue  # 이미 저장된 회차는 건너뜀

        created_at = item["created_at"]
        result = item["result"].replace(",", "-")  # 예: "좌사홀,우삼짝,좌삼짝,우사홀"

        worksheet.append_row([round_number, created_at, result])
        new_count += 1
        print(f"{round_number}회차 저장됨")
    if new_count == 0:
        print("모든 회차가 이미 저장됨")

# 메인 실행
def main():
    print("자동 저장 시작")
    gc = authorize_google_sheets()
    sh = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
    worksheet = sh.worksheet("예측결과")

    saved_rounds = get_saved_rounds(worksheet)
    recent_data = fetch_recent_results()
    save_new_rounds(worksheet, recent_data, saved_rounds)

if __name__ == "__main__":
    main()
