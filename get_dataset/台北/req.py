import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pandas as pd
from tqdm import tqdm

import threading


# 本地代理配置
LOCAL_PROXY = "http://127.0.0.1:7890"

# 配置 WebDriver
def start_browser_with_proxy():
    chrome_options = Options()
    chrome_options.add_argument(f"--proxy-server={LOCAL_PROXY}")
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    service = Service("./chromedriver")  # 替换为你的 ChromeDriver 路径
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# 爬取 f-t 范围的 URL 对应文物
def craw(driver, f, t):
    all_data = []
    try:
        for i in tqdm(range(f, t)):
            uid = i
            try:
                driver.get(f'https://digitalarchive.npm.gov.tw/Antique/Content?uid={i}&Dept=U')
                # 等待数据加载完成
                wait = WebDriverWait(driver, 2)
                tbody_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="collapseExample"]/div/div[1]/table/tbody')))
                tr_elements = tbody_element.find_elements(By.TAG_NAME, "tr")
                image = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ug-item-wrapper')))
                image_url = image.find_element(By.TAG_NAME, 'img').get_attribute("src")

                # 提取数据
                name, category, dynasty, description = '', '', '', ''
                for tr in tr_elements:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    if len(tds) >= 2:
                        label = tds[0].text.strip()
                        value = tds[1].text.strip()
                        if label == '品名':
                            name = value
                        elif label == '分類':
                            category = value
                        elif label == '說明':
                            description = value
                        elif label == '時代':
                            dynasty = value

                dynasty = dynasty if dynasty else ''
                description = description if description else ''
                all_data.append({'ID': uid, 'Name': name, 'Category': category, 'Dynasty': dynasty, 'Description': description, 'Image': image_url})

                time.sleep(1)  # 设置间隔，避免过多请求导致被限制

            except TimeoutException:
                print(f"UID {i}: 加载超时，等待60秒")
                time.sleep(60)
                continue
            except Exception as e:
                print(f"UID {i}: 出现异常，等待60秒")
                time.sleep(60)
                continue

    finally:
        driver.quit()

    return all_data


# 写入 Excel 文件
def to_excel(filename, all_data):
    print(f"共爬取到 {len(all_data)} 条数据")
    df = pd.DataFrame(all_data)
    df.to_excel(filename, index=False)
    print(f"数据已写入到 {filename}")

def main():
    filename = "relics_taiwan.xlsx"
    range_start = 30070
    range_end = 30120
    step = 15  # 每次爬取的步长
    all_data = []

    for i in range(range_start, range_end, step):
        print(f"正在爬取 UID {i} 到 {i + step - 1}...")

        driver = None  # 确保 driver 变量在任何情况下都被定义
        try:
            driver = start_browser_with_proxy()
            batch_data = craw(driver, i, min(i + step, range_end))
            all_data.extend(batch_data)
        except Exception as e:
            print(f"UID {i} 到 {i + step - 1} 爬取失败，原因: {e}")
        finally:
            # 确保 driver 被关闭
            if driver:
                driver.quit()
        time.sleep(60)
    # 写入 Excel 文件
    to_excel(filename, all_data)
    print(f"完成所有爬取，数据已保存到 {filename}")

if __name__ == '__main__':
    main()