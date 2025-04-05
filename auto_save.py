import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = json.loads(os.environ["GOOGLE_SHEET_JSON"])
credentials = Credentials.from_service_account_info(json_data, scopes=scope)
gc = gspread.authorize(credentials)

# 시트 열기
spreadsheet = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = spreadsheet.worksheet("예측결과")

# 최신 저장된 회차 확인
def get_latest_round():
    records = worksheet.get_all_values()
    if len(records) > 1:
        last_row = records[-1]
        return last_row[1]  # 두 번째 열: 회차 번호
    return None

# 실시간 데이터 불러오기
def fetch_recent_results():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"회차 데이터 불러오기 실패: {response.status_code}")
        return []

# 시트에 저장
def save_result_to_sheet(result):
    reg_date = result["reg_date"]
    date_round = result["date_round"]
    start_point = result["start_point"]
    line_count = result["line_count"]
    odd_even = result["odd_even"]
    worksheet.append_row([reg_date, date_round, start_point, line_count, odd_even])
    print("✅ 시트에 저장 완료:", reg_date, date_round)

# 메인 실행
def main():
    print("🔄 자동 저장 시작")
    latest_round = get_latest_round()
    results = fetch_recent_results()

    if not results:
        print("⚠️ 가져온 데이터 없음")
        return

    current_result = results[0]  # 가장 최신 회차
    current_round = str(current_result["date_round"])  # 문자열로 변환
    
    if current_round != latest_round:
        save_result_to_sheet(current_result)
    else:
        print("ℹ️ 이미 저장된 회차:", current_round)

if __name__ == "__main__":
    import os
    main()
