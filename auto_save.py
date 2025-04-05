import requests
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 환경변수에서 키 읽기
import os
import base64

print("백그라운드 작업 실행 중...")

# Google 인증 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
json_str = os.getenv("GOOGLE_SHEET_JSON")
service_account_info = json.loads(json_str)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(credentials)

# 구글 시트 연결
sheet = client.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = sheet.worksheet("예측결과")

def fetch_recent_results():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    print("응답 상태 코드:", response.status_code)

    if response.status_code != 200:
        print("❌ 요청 실패:", response.status_code)
        return []

    try:
        return response.json()
    except json.decoder.JSONDecodeError:
        print("❌ JSON 디코딩 오류 - 응답 내용:", response.text)
        return []

def get_last_saved_round():
    try:
        values = worksheet.col_values(2)  # 2번째 열 = 회차
        if len(values) <= 1:
            return 0
        return int(values[-1])  # 마지막 저장된 회차
    except:
        return 0

def save_new_result(data):
    last_round = get_last_saved_round()
    print("가장 마지막 저장된 회차:", last_round)

    for row in reversed(data):
        round_no = int(row['date_round'])
        if round_no > last_round:
            values = [
                row['date_round'],
                row['reg_date'],
                row['start_point'],
                row['line_count'],
                row['odd_even']
            ]
            worksheet.append_row(values)
            print("✅ 새 회차 저장 완료:", round_no)
            break
        else:
            print("🔁 이미 저장된 회차:", round_no)

def main():
    recent_data = fetch_recent_results()
    if recent_data:
        save_new_result(recent_data)
    else:
        print("⚠️ 가져온 데이터가 올바르지 않습니다.")

if __name__ == "__main__":
    main()
