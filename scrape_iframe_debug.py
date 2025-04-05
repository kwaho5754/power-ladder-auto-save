from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# 브라우저 꺼짐 없이 실행하고 싶으면 주석 해제 (개발 중 디버깅에 좋음)
# options = Options()
# options.add_argument("--headless")

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# 크롬드라이버 경로
driver_path = "./chromedriver.exe"
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

try:
    url = "https://ntry.com/stats/power_ladder/pattern.php"
    driver.get(url)
    time.sleep(3)

    # iframe 수 확인
    iframes = driver.find_elements("tag name", "iframe")
    print(f"iframe 개수: {len(iframes)}")

    for i, iframe in enumerate(iframes):
        driver.switch_to.frame(iframe)
        time.sleep(1)
        html = driver.page_source
        with open(f"iframe_debug_{i}.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ iframe {i} 저장 완료 (iframe_debug_{i}.html)")
        driver.switch_to.default_content()

finally:
    driver.quit()


