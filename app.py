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

@app.route("/run-manual")
def run_predict():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()
        now = datetime.now()

        reverse_map = {
            "좌삼짝": "우사홀",
            "우삼홀": "좌사짝",
            "좌사홀": "우삼홀",
            "우사짝": "좌삼짝"
        }

        all_combos = []
        valid_combos = []
        recent_items = []

        for item in data:
            time_str = str(item["reg_date"])
            if len(time_str) == 10:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d")
            else:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                all_combos.append(combo)
                if combo != "기타":
                    valid_combos.append(combo)
                    recent_items.append(item)

        all_counter = Counter(all_combos)
        valid_counter = Counter(valid_combos)

        html = ""
        if recent_items:
            last_round_number = int(recent_items[-1]["round"])
            next_round_number = last_round_number + 1
            html += f"<p>📅 최근 결과 회차: {last_round_number}회차</p>"
            html += f"<h2>🎯 예측 결과 ({next_round_number}회차 예상)</h2>"

        combo_score = {}
        for combo in valid_counter:
            base = valid_counter[combo]
            reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base + reverse

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

        for i, (combo, n) in enumerate(top3, 1):
            html += f"<p>✅ {i}위 예측: <b>{combo}</b></p>"

        html += f"<p>✅ 유효 조합 개수: {len(valid_combos)}</p>"

        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
