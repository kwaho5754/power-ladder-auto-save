import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageFilter, ImageEnhance
import pytesseract
import os

# Tesseract 실행 경로 설정 (본인 PC에 설치된 경로로 수정)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Chrome 옵션 설정
options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# 브라우저 열기 및 페이지 접속
print("📌 페이지 접속 중...")
driver = webdriver.Chrome(options=options)
driver.get("https://ntry.com/stats/power_ladder/pattern.php")

# 잠시 대기 후 전체 페이지 스크린샷 저장
time.sleep(5)
screenshot_path = 'pattern_page.png'
driver.save_screenshot(screenshot_path)
print("🗄 화면 캡처 완료:", screenshot_path)

# Selenium 브라우저 닫기
driver.quit()

# 이미지 열기 및 전처리
image = Image.open(screenshot_path)
image = image.convert("L")  # 흑백 변환
image = image.filter(ImageFilter.MedianFilter())
enhancer = ImageEnhance.Contrast(image)
image = enhancer.enhance(2)  # 대비 높이기

# OCR 인식
print("🔍 OCR 인식 결과:")
text = pytesseract.image_to_string(image, lang='kor+eng')
print(text)

# 결과를 텍스트 파일로 저장 (선택사항)
with open("pattern_ocr_result.txt", "w", encoding="utf-8") as f:
    f.write(text)
    print("\n🔖 OCR 결과 저장 완료: pattern_ocr_result.txt")
