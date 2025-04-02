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
                    recent_items.append((item.get("round", "??회차"), combo))

        all_counter = Counter(all_combos)
        valid_counter = Counter(valid_combos)

        html = "<h2>📊 최근 24시간 기준 분석 결과 (본인 + 반대 포함)</h2>"
        for combo in ["좌삼짝", "우삼홀", "좌사홀", "우사짝"]:
            valid_count = valid_counter.get(combo, 0)
            total_count = all_counter.get(combo, 0)
            html += f"✅ {combo}: {valid_count}회 (전체: {total_count}회)<br>"

        combo_score = {}
        for combo in valid_counter:
            base = valid_counter[combo]
            reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base + reverse

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

        html += "<h2>🎯 예측 결과 (최근 24시간 분석 기반)</h2>"
        for i, (combo, _) in enumerate(top3, 1):
            html += f"✅ {i}위 예측: <b>{combo}</b><br>"

        html += f"<p>✅ 유효 조합 개수: {len(valid_combos)}</p>"

        html += "<h2>📜 24시간 전체 결과 출력</h2>"
        for round_, combo in reversed(recent_items):
            html += f"- {round_} ➜ 조합: {combo}<br>"

        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
