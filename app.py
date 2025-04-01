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
        return "좌삼짹"
    elif start == "right" and line == 3 and odd == "odd":
        return "우삼홀"
    elif start == "left" and line == 4 and odd == "odd":
        return "좌사홀"
    elif start == "right" and line == 4 and odd == "even":
        return "우사짹"
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
            "좌삼짹": "우사홀",
            "우삼홀": "좌삼짹",
            "좌사홀": "우사짹",
            "우사짹": "좌사홀"
        }

        all_combos = []
        valid_combos = []
        reg_dates = []

        for item in data:
            reg_time = datetime.strptime(item["reg_date"], "%Y-%m-%d") if len(item["reg_date"]) == 10 else datetime.strptime(item["reg_date"], "%Y-%m-%d %H:%M:%S")
            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                all_combos.append(combo)
                if combo != "기타":
                    valid_combos.append(combo)
                    reg_dates.append(reg_time)

        html = "<h2>현재 24시간 기준 배후 결과 (본인 + 반대 포함)</h2>"
        all_counter = Counter(all_combos)
        valid_counter = Counter(valid_combos)
        for combo in ["좌삼짹", "우삼홀", "좌사홀", "우사짹"]:
            html += f"<p>- {combo}: {valid_counter[combo]}회 (전체: {all_counter[combo]}회)</p>"

        html += "<h2>형태변화 구조 기본 예측 결과</h2>"

        combo_score = {}
        for combo in valid_counter:
            base = valid_counter[combo]
            reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base * 2 + reverse

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (combo, score) in enumerate(top3, 1):
            html += f"<p>✅ {i}위 예측: <b>{combo}</b></p>"

        html += f"<p>\n후복 조합 수 (전체): {len(valid_combos)} / 전체: {len(all_combos)}</p>"

        # 고급 분석 포함
        html += "<h2>고급 분석 패턴 확장</h2>"

        # 1. 반복 패턴 구간 추출
        from itertools import groupby
        group_counts = [len(list(group)) for _, group in groupby(valid_combos)]
        max_repeat = max(group_counts)
        most_recent_repeat = group_counts[-1] if group_counts else 0
        html += f"<p>♻ 다시 반복된 조합 기간 최대: {max_repeat}회 / 현재 연속: {most_recent_repeat}회</p>"

        # 4. 예측 정확도 기록 (간절)
        html += f"<p>현재 예측된 조합은 없음. 정확도 기록 보호는 최규 목표</p>"

        # 5. 무드롭 조합 감지
        rare_combos = [combo for combo in ["좌삼짹", "우삼홀", "좌사홀", "우사짹"] if valid_counter[combo] == 0]
        if rare_combos:
            html += f"<p>현재 무드롭 (아름에도 안나온) 조합: {', '.join(rare_combos)}</p>"

        # 6. 패턴 전환 지점 탐지
        transition_points = 0
        for i in range(1, len(valid_combos)):
            if valid_combos[i] != valid_combos[i - 1]:
                transition_points += 1
        html += f"<p>패턴 전환 지점 수: {transition_points}</p>"

        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
