from flask import Flask
import requests
from datetime import datetime
from collections import Counter

app = Flask(__name__)

def extract_combination(item):
    start = str(item["start_point"]).lower()
    line = int(item["line_count"])
    odd = str(item["odd_even"]).lower()

    if start == "left" and line == 3 and odd == "even":
        return "좌삼짝"
    elif start == "right" and line == 3 and odd == "odd":
        return "우삼홀"
    elif start == "left" and line == 4 and odd == "odd":
        return "좌사홀"
    elif start == "right" and line == 4 and odd == "even":
        return "우사짝"
    else:
        return "기타"

@app.route("/run-predict")
def run_predict():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()
        now = datetime.now()

        reverse_map = {
            "좌삼짝": "우삼홀",
            "우삼홀": "좌삼짝",
            "좌사홀": "우사짝",
            "우사짝": "좌사홀"
        }

        all_combos = []  # 전체 조합 저장
        valid_combos = []  # 유효한 조합만 저장

        for item in data:
            reg_time = datetime.strptime(item["reg_date"], "%Y-%m-%d %H:%M:%S")
            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                all_combos.append(combo)  # 전체 기록
                if combo != "기타":
                    valid_combos.append(combo)  # 유효 기록

        all_counter = Counter(all_combos)
        valid_counter = Counter(valid_combos)

        html = f"<h2>📆 최근 24시간 조합 분석 결과 (본인 + 반대 포함)</h2>"
        for combo in ["좌삼짝", "우삼홀", "좌사홀", "우사짝"]:
            valid_count = valid_counter.get(combo, 0)
            total_count = all_counter.get(combo, 0)
            html += f"<p>- {combo}: {valid_count}회 (전체: {total_count}회)</p>"

        # 예측 로직 (유효 조합만 기반)
        combo_score = {}
        for combo in valid_counter:
            base = valid_counter[combo]
            reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base + reverse

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

        html += f"<h2>🔹 예측 결과 (거주 24시간 기준)</h2>"
        for i, (combo, _) in enumerate(top3, 1):
            html += f"<p>✅ {i}위 예측: <b>{combo}</b></p>"

        html += f"<p>📆 모든 그룹 포함 합계: {len(all_combos)}개</p>"
        html += f"<p>📅 유효 조합수: {len(valid_combos)}개</p>"

        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
