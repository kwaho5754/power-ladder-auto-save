import requests
import json
from datetime import datetime

# ✅ 현재 시각 출력
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"🟢 [Now] - 자동 예측 실행 중...")

# ✅ 파워사다리 최신 결과 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
try:
    response = requests.get(url)
    data = response.json()
    round_number = data[0]["round"]  # ✅ 리스트 첫 번째 요소의 딕셔너리에서 접근
    print(f"✅ 현재 회차: {round_number}")
except Exception as e:
    print(f"❌ 오류: 실시간 데이터 불러오기 실패 - {e}")
    exit()

# ✅ 예측 (단순 예시)
ranking = ["좌삼짝", "우삼홀", "좌사홀"]
print("📊 예측 결과")
print(f"🥇 1위: {ranking[0]}")
print(f"🥈 2위: {ranking[1]}")
print(f"🥉 3위: {ranking[2]}")
