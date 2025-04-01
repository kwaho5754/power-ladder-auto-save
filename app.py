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

def analyze_patterns(items):
    pattern_analysis = "<h3>🧠 고급 패턴 분석</h3>"
    if not items:
        return pattern_analysis + "<p>데이터 없음</p>"

    recent_10 = items[-10:]

    combo_list = [item['combo'] for item in recent_10 if item['combo'] != '기타']
    last_combo = None
    streak = 0
    longest_combo = None
    longest_streak = 0
    non_appeared = {"좌삼짝", "우삼홀", "좌사홀", "우사짝"}

    for combo in combo_list:
        if combo in non_appeared:
            non_appeared.discard(combo)
        if combo == last_combo:
            streak += 1
        else:
            if streak > longest_streak:
                longest_streak = streak
                longest_combo = last_combo
            last_combo = combo
            streak = 1

    if streak > longest_streak:
        longest_streak = streak
        longest_combo = last_combo

    if longest_combo:
        pattern_analysis += f"<p>🔁 최근 10회 중 가장 반복된 조합: <b>{longest_combo}</b> ({longest_streak}회 연속)</p>"
        if longest_streak >= 3:
            reverse_map = {
                "좌삼짝": "우삼홀",
                "우삼홀": "좌삼짝",
                "좌사홀": "우사짝",
                "우사짝": "좌사홀"
            }
            expected_reverse = reverse_map.get(longest_combo, "없음")
            pattern_analysis += f"<p>➡️ 예상 반대 조합 등장 가능성: <b>{expected_reverse}</b></p>"

    if non_appeared:
        missed = ", ".join(non_appeared)
        pattern_analysis += f"<p>📉 최근 10회 동안 등장하지 않은 조합: {missed}</p>"

    # 추가 분석: 홀/짝, 줄 수, 좌/우
    odds = [item['odd_even'] for item in recent_10 if item['odd_even'] in ('홀', '짝')]
    lines = [str(item['line_count']) for item in recent_10 if str(item['line_count']) in ('3', '4')]
    sides = [item['start_point'] for item in recent_10 if item['start_point'] in ('왼쪽', '오른쪽')]

    if odds:
        last_odd = odds[-1]
        odd_streak = len(list(reversed(list(takewhile(lambda x: x == last_odd, reversed(odds))))))
        pattern_analysis += f"<p>⚖️ 최근 홀/짝: <b>{last_odd}</b> {odd_streak}회 연속</p>"

    if lines:
        last_line = lines[-1]
        line_streak = len(list(reversed(list(takewhile(lambda x: x == last_line, reversed(lines))))))
        pattern_analysis += f"<p>📏 최근 줄 수: <b>{last_line}</b>줄 {line_streak}회 연속</p>"

    if sides:
        last_side = sides[-1]
        side_streak = len(list(reversed(list(takewhile(lambda x: x == last_side, reversed(sides))))))
        pattern_analysis += f"<p>↔️ 최근 방향: <b>{last_side}</b> {side_streak}회 연속</p>"

    return pattern_analysis

def takewhile(predicate, iterable):
    for item in iterable:
        if predicate(item):
            yield item
        else:
            break

def get_prediction_html():
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

    all_combos = []
    valid_combos = []
    recent_items = []

    for item in data:
        time_str = item["reg_date"]
        if len(time_str) == 10:
            reg_time = datetime.strptime(time_str, "%Y-%m-%d")
        else:
            reg_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        if (now - reg_time).total_seconds() <= 86400:
            combo = extract_combination(item)
            item["combo"] = combo
            all_combos.append(combo)
            if combo != "기타":
                valid_combos.append(combo)
            recent_items.append(item)

    all_counter = Counter(all_combos)
    valid_counter = Counter(valid_combos)

    html = "<h2>📚 최근 24시간 기준 분석 결과 (본인 + 반대 포함)</h2>"
    for combo in ["좌삼짝", "우삼홀", "좌사홀", "우사짝"]:
        valid_count = valid_counter.get(combo, 0)
        total_count = all_counter.get(combo, 0)
        html += f"<p>➤ {combo}: {valid_count}회 (전체: {total_count}회)</p>"

    combo_score = {}
    for combo in valid_counter:
        base = valid_counter[combo]
        reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
        combo_score[combo] = base + reverse

    top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

    html += "<h2>🎯 예측 결과 (최근 24시간 분석 기반)</h2>"
    for i, (combo, _) in enumerate(top3, 1):
        html += f"<p>✅ {i}위 예측: <b>{combo}</b></p>"

    html += f"<p>📊 유효한 조합 총 분석 개수: {len(valid_combos)} / 전체: {len(all_combos)}</p>"
    html += analyze_patterns(recent_items)

    return html

@app.route("/run-predict")
def run_predict():
    try:
        return get_prediction_html()
    except Exception as e:
        return f"<p>⚠️ 오류 발생: {e}</p>"

@app.route("/run-manual")
def run_manual():
    try:
        return get_prediction_html()
    except Exception as e:
        return f"<p>⚠️ 오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
