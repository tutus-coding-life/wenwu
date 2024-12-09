from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置Chrome选项以无头模式运行（可选）
chrome_options = Options()
# chrome_options.add_argument("--headless")  # 确保GUI不出现在前台

# 指定ChromeDriver的路径（根据你的安装位置调整）
service = Service('./chromedriver')

# 创建一个新的浏览器实例
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # 访问目标网页
    url = 'https://digitalarchive.npm.gov.tw/Antique/Content?uid=30064&Dept=U'  # 替换为实际URL
    driver.get(url)

    # 等待特定元素出现，确保页面已经加载完毕
    wait = WebDriverWait(driver, 2)
    tbody_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="collapseExample"]/div/div[1]/table/tbody')))
    # print(tbody_element.text)
    # # 提取所需信息
    tr_elements = tbody_element.find_elements(By.TAG_NAME, "tr")
    for tr in tr_elements:
        # print(tr.text)
        tds = tr.find_elements(By.TAG_NAME, "td")
        if len(tds) >= 2:
            label = tds[0].text.strip()
            value = tds[1].text.strip()
            # print(label, value)
            if label == '品名':
                print('品名:', value)
            elif label == '分類':
                print('分類:', value)
            elif label == '說明':
                print('說明:', value)
            elif label == '時代':
                print('時代:', value)
            elif label == '說明‘':
                print('說明:', value)
    if '時代' not in [tr.find_elements(By.TAG_NAME, "td")[0].text.strip() for tr in tr_elements]:
        print('時代:')            
    # 如果說明不在label中，输出一个空白项
    if '說明' not in [tr.find_elements(By.TAG_NAME, "td")[0].text.strip() for tr in tr_elements]:
        print('說明:')

finally:
    # 关闭浏览器
    driver.quit()