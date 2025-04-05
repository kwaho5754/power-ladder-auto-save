import requests
import json

def fetch_pattern_data():
    url = "https://ntry.com/data/json/games/power_ladder/pattern.json"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 처리

        data = response.json()
        print("✅ 패턴 데이터 수집 성공!")
        print(json.dumps(data[:3], indent=2, ensure_ascii=False))  # 앞 3개 데이터만 출력 (확인용)

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    fetch_pattern_data()
