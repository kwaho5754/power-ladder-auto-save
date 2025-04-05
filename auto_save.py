import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from datetime import datetime

# 환경 변수에서 서비스 계정 JSON 로드
json_str = os.getenv("GOOGLE_SHEET_JSON")
service_account_info = json.loads(json_str)

# Google Sheets 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

# 시트 열기
spreadsheet = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = spreadsheet.worksheet("예측결과")

# 최근 결과 가져오기 함수 (User-Agent 추가)
def fetch_recent_results():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    print("응답 상태 코드:", response.status_code)
    print("응답 내용:", response.text)
    return response.json()

# 시트에 이미 저장된 회차 번호 가져오기
def get_saved_rounds():
    data = worksheet.get_all_values()
    return {row[0] for row in data[1:]}  # 첫 행은 헤더

# 시트에 저장
def save_to_sheet(result):
    saved_rounds = get_saved_rounds()
    round_num = str(result["round"])
    if round_num in saved_rounds:
        print(f"이미 저장된 회차: {round_num}")
        return

    date = result["date"]
    ladder = result["ladder"]
    left_right = ladder["position"]
    count = ladder["count"]
    parity = ladder["parity"]
    
    new_row = [round_num, date, left_right, count, parity]
    worksheet.append_row(new_row)
    print(f"✅ 저장 완료: {new_row}")

# 메인 실행
def main():
    recent_data = fetch_recent_results()
    if isinstance(recent_data, dict):
        save_to_sheet(recent_data)
    else:
        print("⚠️ 가져온 데이터가 올바르지 않습니다.")

if __name__ == "__main__":
    main()

