import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os  # ← 이 부분 중요!

# 구글 인증
def authenticate_google_sheets():
    try:
        json_str = os.environ.get("GOOGLE_SHEET_JSON")
        if json_str is None:
            raise ValueError("환경변수 GOOGLE_SHEET_JSON 없음")
        with open("cred.json", "w") as f:
            f.write(json_str)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("cred.json", scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print("❗ 구글 인증 실패:", e)
        return None

# 실시간 회차 데이터 요청
def fetch_recent_results():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("✅ 응답 상태 코드:", response.status_code)
        return response.json()  # 결과는 리스트
    except Exception as e:
        print("⚠️ 회차 데이터 불러오기 실패:", e)
        return []

# 시트에서 마지막 저장 회차 확인
def get_last_round(sheet):
    values = sheet.get_all_values()
    if len(values) < 2:
        return 0
    return int(values[-1][1])  # 두 번째 열이 회차

# 시트에 저장
def save_to_sheet(sheet, data):
    try:
        new_row = [
            data["reg_date"],
            data["date_round"],
            data["start_point"],
            data["line_count"],
            data["odd_even"]
        ]
        sheet.append_row(new_row)
        print("✅ 저장 완료:", new_row)
    except Exception as e:
        print("❗ 저장 실패:", e)

# 메인 실행
def main():
    print("🔄 자동 저장 시작")
    client = authenticate_google_sheets()
    if client is None:
        return

    sheet = client.open("실시간결과").worksheet("예측결과")
    latest_result = fetch_recent_results()

    if not latest_result:
        print("ℹ️ 저장할 데이터 없음")
        return

    current_round = int(latest_result[0]["date_round"])
    last_saved_round = get_last_round(sheet)

    if current_round > last_saved_round:
        print(f"🆕 새 회차 감지됨: {current_round}")
        save_to_sheet(sheet, latest_result[0])
    else:
        print("ℹ️ 저장할 새 회차 없음")

if __name__ == "__main__":
    main()
