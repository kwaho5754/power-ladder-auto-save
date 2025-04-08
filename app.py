from flask import Flask
import os
import json
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# ✅ 구글 시트 연동 설정
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
if not SERVICE_ACCOUNT_JSON:
    raise ValueError("SERVICE_ACCOUNT_JSON 환경변수가 없습니다.")
info = json.loads(SERVICE_ACCOUNT_JSON)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
gc = gspread.authorize(credentials)

# ✅ 시트 정보
SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
WORKSHEET_NAME = "예측결과"

@app.route('/predict')
def predict():
    # 시트 데이터 가져오기
    worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)
    data = worksheet.get_all_values()[1:]  # 헤더 제외

    if len(data) < 10:
        return "데이터가 부족합니다."

    df = pd.DataFrame(data, columns=["date", "round", "좌우", "줄수", "홀짝"])

    # 최근 30줄 기준 분석
    recent = df.tail(30)

    # 조합별 카운트
    recent["조합"] = recent["좌우"] + recent["줄수"] + recent["홀짝"]
    counts = recent["조합"].value_counts()

    top3 = counts.head(3).index.tolist()

    return f"""
    ✅ 최근 회차 기준 예측 결과<br>
    1위: {top3[0]}<br>
    2위: {top3[1]}<br>
    3위: {top3[2]}<br>
    (최근 30줄 기준 분석)
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
