import os
import pandas as pd
import gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    # 서비스 계정 JSON을 환경변수에서 읽음
    service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

    # 환경변수 값을 JSON 파일로 저장
    with open("service_account.json", "w") as f:
        f.write(service_account_json)

    # 구글 시트 인증
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(credentials)

    # 구글 시트 열기
    spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
    worksheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")
    data = worksheet.get_all_records()

    if not data:
        return "데이터가 없습니다."

    df = pd.DataFrame(data)

    # 열 이름이 한국어 기준일 때 정확하게 사용해야 함
    df = df.rename(columns={
        "날짜": "reg_date",
        "회차": "date_round",
        "방향": "start_point",
        "줄수": "line_count",
        "홀짝": "odd_even"
    })

    # 최신 회차
    latest_round = df["date_round"].max()

    # 최근 30줄 분석
    recent_data = df.sort_values(by="date_round", ascending=False).head(30)
    recent_data["조합"] = recent_data["start_point"] + recent_data["line_count"].astype(str) + recent_data["odd_even"]

    counts = Counter(recent_data["조합"])
    top_3 = counts.most_common(3)

    response = "✅ 최근 회차 기준 예측 결과<br>"
    for i, (combo, _) in enumerate(top_3, start=1):
        response += f"{i}위: {combo}<br>"
    response += f"(최근 30줄 기준 분석)<br>"
    response += f"예측 기준 회차: {latest_round + 1}회차"

    return response
