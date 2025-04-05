from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 크롬 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)
url = "https://ntry.com/stats/power_ladder/pattern.php"
driver.get(url)
print("📌 페이지 접속 완료...")

try:
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "iframe")))
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"🧩 iframe 개수: {len(iframes)}")

    for idx, iframe in enumerate(iframes):
        driver.switch_to.default_content()
        driver.switch_to.frame(iframe)
        print(f"🔍 iframe {idx} 진입 완료")

        # 👇 HTML 전체 구조 출력
        html = driver.page_source
        with open(f"iframe_{idx}_html_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ iframe {idx} 구조를 iframe_{idx}_html_dump.html 로 저장 완료")

    print("📁 HTML 저장 완료. VS Code에서 열어보고 정확한 셀렉터 확인해보세요.")

except Exception as e:
    print("❌ 오류 발생:", str(e))

driver.quit()
