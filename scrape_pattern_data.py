from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(executable_path="./chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

url = "https://ntry.com/stats/power_ladder/pattern.php"
driver.get(url)

print("✅ 페이지 접속 완료. 로딩 대기 중...")
time.sleep(10)

print("iframe 개수:", len(driver.find_elements('tag name', 'iframe')))
print("페이지 타이틀:", driver.title)

# ▶ iframe 전환
iframe = driver.find_elements('tag name', 'iframe')[0]
driver.switch_to.frame(iframe)

# ▶ 전환 후 HTML 파싱
soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.select_one(".pattern_tb")

if not table:
    print("❌ 패턴 테이블을 찾지 못했습니다.")
    driver.quit()
    exit()

# ▶ 테이블 파싱
rows = table.select("tbody tr")
pattern_data = []

for row in rows:
    cols = row.select("td")
    if len(cols) >= 5:
        date = cols[0].get_text(strip=True)
        round_ = cols[1].get_text(strip=True)
        result = cols[4].get_text(strip=True)
        pattern_data.append((date, round_, result))

print(f"✅ 총 {len(pattern_data)}개 수집됨")
for item in pattern_data:
    print(item)

driver.quit()
