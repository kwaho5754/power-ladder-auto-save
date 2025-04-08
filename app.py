from flask import Flask
import pandas as pd
import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route("/predict")
def predict():
    # 환경 변수에서 JSON 가져오기
    import json
    service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")
    keyfile_dict = json.loads(service_account_json)

    # 구글 시트 접근
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(keyfile_dict, scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
    worksheet = spreadsheet.worksheet("예측결과")

    # 시트 데이터 가져오기
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # 회차 기준 최근 30줄
    df = df.sort_values(by="date_round", ascending=False)
    recent_df = df.head(30)

    # 조합 문자열 생성
    recent_df["조합"] = recent_df["start_point"] + recent_df["line_count"].astype(str) + recent_df["odd_even"]

    # 빈도 분석
    top_3 = recent_df["조합"].value_counts().head(3).index.tolist()

    # 최신 회차 기준 추정
    latest_round = df["date_round"].max() + 1

    # 결과 출력
    result = "✅ 최근 회차 기준 예측 결과 (진행 중인 회차: {})\n".format(latest_round)
    for i, comb in enumerate(top_3, start=1):
        result += f"{i}위: {comb}\n"
    result += "(최근 30줄 기준 분석)"

    return result
