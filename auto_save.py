import requests
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def fetch_latest_result():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        data = response.json()
        print("✅ 응답 상태 코드:", response.status_code)
        print("✅ 응답 내용:", data)
        return data
    except Exception as e:
        print("❌ 회차 데이터 불러오기 실패:", e)
        return None

def load_credentials():
    try:
        json_data = os.environ.get("GOOGLE_SHEET_JSON")
        if not json_data:
            raise ValueError("환경변수 GOOGLE_SHEET_JSON 없음")
        info = json.loads(json_data)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
        return gspread.authorize(credentials)
    except Exception as e:
        print("❌ 구글 인증 실패:", e)
        return None

def get_last_saved_round(sheet):
    try:
        values = sheet.get_all_values()
        if len(values) < 2:
            return 0
        return int(values[-1][1])  # 두 번째 열 = 회차 번호
    except Exception as e:
        print("❌ 마지막 저장 회차 확인 실패:", e)
        return 0

def save_result_to_sheet(sheet, result):
    try:
        sheet.append_row([
            result.get("date", ""),
            result.get("round", ""),
            result.get("result", {}).get("odd_even", ""),
            result.get("result", {}).get("start_point", ""),
            result.get("result", {}).get("line_count", "")
        ])
        print("✅ 저장 완료:", result)
    except Exception as e:
        print("❌ 시트 저장 실패:", e)

def main():
    print("📌 자동 저장 시작")
    result = fetch_latest_result()
    if result is None:
        return

    gc = load_credentials()
    if gc is None:
        return

    try:
        sh = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
        sheet = sh.worksheet("예측결과")
    except Exception as e:
        print("❌ 구글 시트 열기 실패:", e)
        return

    last_saved = get_last_saved_round(sheet)
    current_round = result.get("round", 0)
    print("📌 가장 마지막 저장된 회차:", last_saved)
    print("📌 현재 회차:", current_round)

    if current_round > last_saved:
        save_result_to_sheet(sheet, result)
    else:
        print("ℹ️ 저장할 새 회차 없음")

if __name__ == "__main__":
    main()
