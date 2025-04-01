from flask import Flask
import requests
from datetime import datetime
from collections import Counter

app = Flask(__name__)

def extract_combination(item):
    try:
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
    except:
        return "기타"

@app.route("/run-manual")
def run_manual():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()
        now = datetime.now()

        reverse_map = {
            "좌삼짝": "우삼홀",
            "우삼홀": "좌삼짝",
            "좌사홀": "우사짝",
            "우사짝": "좌사홀",
        }

        all_combos = []
        valid_combos = []
        recent_items = []

        for item in data:
            try:
                reg_time = datetime.strptime(item["reg_date"], "%Y-%m-%d %H:%M:%S")
            except:
                try:
                    reg_time = datetime.strptime(item["reg_date"], "%Y-%m-%d")
                except:
                    continue

            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                all_combos.append((item.get("reg_date", ""), item.get("round", "??회차"), combo))
                if combo != "기타":
                    valid_combos.append(combo)
                    recent_items.append((item.get("reg_date", ""), item.get("round", "??회차"), combo))

        valid_counter = Counter(valid_combos)
        reverse_counter = Counter([reverse_map.get(c, "") for c in valid_combos if c in reverse_map])

        html = "<h2>📌 예측 결과</h2>"
        top3 = sorted(valid_counter.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (combo, count) in enumerate(top3, 1):
            html += f"✅ {i}위 예측: <b>{combo}</b><br>"

        html += f"<p>✅ 유효 조합 개수: {len(valid_combos)}</p>"

        html += "<hr><h3>📜 24시간 전체 결과 출력</h3>"
        for reg_date, round_, combo in recent_items[::-1]:  # 최신 → 오래된 순
            html += f"- {reg_date} / {round_} ➜ 조합: {combo}<br>"

        return html

    except Exception as e:
        return f"<p>❌ 오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
