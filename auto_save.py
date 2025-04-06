import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# ✅ 환경변수에서 서비스 계정 키 불러와 파일로 저장
SERVICE_ACCOUNT_KEY = os.environ.get("GOOGLE_SHEET_JSON")

with open("service_account.json", "w") as f:
    f.write(SERVICE_ACCOUNT_KEY)

# ✅ 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=scope)
gc = gspread.authorize(creds)

# ✅ 시트 열기
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = gc.open_by_key(spreadsheet_id).worksheet("예측결과")

# ✅ 데이터 URL
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

# ✅ 저장 함수 정의
def save_to_sheet(data):
    try:
        row = [
            data["reg_date"],
            data["date_round"],
            data["start_point"],
            data["line_count"],
            data["odd_even"]
        ]
        worksheet.append_row(row)
        print("✅ 저장 완료:", row)
    except Exception as e:
        print("❌ 저장 실패:", e)

# ✅ 메인 실행 함수 (최근 3회차 확인)
def main():
    print("⏰ 자동 저장 시작")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()["rows"][-3:]  # 최근 3회차만
    except Exception as e:
        print("❌ 데이터 요청 실패:", e)
        return

    existing = worksheet.col_values(2)  # 회차 기준 (2열) 중복 방지

    for d in data:
        round_ = str(d["date_round"])
        if round_ not in existing:
            save_to_sheet(d)
        else:
            print(f"🔁 이미 저장된 회차입니다: {round_}")

# ✅ 실행
if __name__ == "__main__":
    main()
