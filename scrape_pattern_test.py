from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium_stealth import stealth  # 설치 필요

# 크롬 옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# 드라이버 실행
driver = webdriver.Chrome(options=options)

# Stealth 적용
stealth(driver,
        languages=["ko-KR", "ko"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

driver.get("https://ntry.com/stats/power_ladder/pattern.php")

# 충분히 기다리기 (10초 이상)
time.sleep(10)

# 확인용 화면 캡처
driver.save_screenshot("pattern_page_result.png")
print("✅ 화면 캡처 완료: pattern_page_result.png")

driver.quit()

