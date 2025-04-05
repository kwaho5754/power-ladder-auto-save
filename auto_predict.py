import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask

app = Flask(__name__)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_sheet_key.json", scope)
client = gspread.authorize(creds)

# 시트 정보
SHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

@app.route("/")
def index():
    return "Power Ladder Auto Save Service"

@app.route("/save", methods=["GET"])
def save_data():
    # JSON 데이터 요청
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    response = requests.get(url)
    data = response.json()

    # 시트에서 마지막 회차 가져오기
    records = sheet.get_all_records()
    existing_rounds = {str(row["회차"]) for row in records if "회차" in row}

    # 저장할 데이터 구성
    new_data = []
    for row in data["rows"]:
        round_no = str(row["round"])
        if round_no not in existing_rounds:
            new_data.append([
                row["date"],
                row["round"],
                row["time"],
                row["start_ladder"],
                row["ladder_count"],
                row["result"]
            ])

    # 저장
    if new_data:
        sheet.append_rows(new_data)
        return f"{len(new_data)}개 저장됨"
    return "중복 없음"

if __name__ == "__main__":
    app.run()
