from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# ChromeDriver 설정
options = Options()
options.add_argument('--headless')  # 브라우저 창 안 보이게
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# 접속할 패턴 페이지
url = "https://ntry.com/stats/power_ladder/pattern.php"
driver.get(url)
time.sleep(3)  # 페이지 로딩 대기

# HTML 내 테이블에서 패턴 정보 추출
pattern_data = []

rows = driver.find_elements(By.CSS_SELECTOR, 'div.pattern_table > div.pattern_row')
for row in rows:
    cells = row.find_elements(By.CSS_SELECTOR, 'div.pattern_cell')
    if len(cells) >= 4:
        try:
            holjjak = cells[0].text.strip()  # 홀/짝
            left_right = cells[1].text.strip()  # 좌/우
            start_dir = cells[2].text.strip()  # 시작 방향
            ladder_count = cells[3].text.strip()  # 사다리 수

            pattern_data.append({
                '홀짝': holjjak,
                '좌우': left_right,
                '시작방향': start_dir,
                '사다리수': ladder_count
            })
        except:
            continue

# 결과 출력
for p in pattern_data:
    print(p)

driver.quit()
