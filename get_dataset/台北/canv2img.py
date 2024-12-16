from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import base64
import io

# 配置 WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式
service = Service("./chromedriver")  # 替换为你的 ChromeDriver 路径
driver = webdriver.Chrome(service=service, options=chrome_options)

# 打开目标页面
url = "https://digitalarchive.npm.gov.tw/Antique/IIIFViewer?uid=30070&Dept=U"  # 替换为包含 canvas 的网页地址
driver.get(url)

try:
    # 使用 CSS_SELECTOR 找到指定的 <canvas> 元素
    wait = WebDriverWait(driver, 10)
    # canvas = wait.until(
    #     EC.presence_of_element_located(
    #         (By.CSS_SELECTOR, 'canvas[role="img"][aria-label="Digitized view"]')
    #     )
    # )
    canvas = driver.find_elements(By.CSS_SELECTOR, 'canvas')[0]  # 第一个 canvas 元素
    # 提取 <canvas> 数据为 Base64 格式
    image_data = driver.execute_script("return arguments[0].toDataURL('image/png');", canvas)

    # 去掉前缀 'data:image/png;base64,'
    base64_data = image_data.split(",")[1]

    # 解码 Base64 数据并保存为 PNG 图片
    image = Image.open(io.BytesIO(base64.b64decode(base64_data)))
    image.save("canvas_image.png")

    print("Canvas 图片已保存为 canvas_image.png")

except Exception as e:
    print(f"出错了: {e}")

finally:
    # 关闭浏览器
    driver.quit()