import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
import pandas as pd
from openpyxl import load_workbook
from tqdm import tqdm


class RelicOverview_taiwan:
    def __init__(self, id, name, category, culturalRelicNo, dynasty, centerImage, description):
        self.id = id
        self.name = name
        self.categoryName = category
        self.culturalRelicNo = culturalRelicNo
        self.dynastyName = dynasty
        self.centerImage = centerImage
        self.description = description

    def __str__(self):
        return f"Name: {self.name}, Category: {self.categoryName}, Dynasty: {self.dynastyName}, Description: {self.description}, Image: {self.centerImage}"
# 创建浏览器实例
def start_browser():
    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-error')
    chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--headless')
    service = Service("./chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# 爬取f-t范围的url对应文物
def craw(driver, f, t, filename):
    uid = -1
    all_data = []
    try:
        for i in tqdm(range(f, t)):
            uid = i
            driver.get(f'https://digitalarchive.npm.gov.tw/Antique/Content?uid={i}&Dept=U')
            try:
                # 等待网页加载，最长等待5秒
                wait = WebDriverWait(driver, 5)
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
                # 如果没有获取到 '時代' 或 '說明' 数据，设为默认空
                if not dynasty:
                    dynasty = ''
                if not description:
                    description = ''

                # 将文物信息添加到 all_data 列表
                all_data.append(RelicOverview_taiwan(i, name, category, '', dynasty, image_url, description))

            except TimeoutException:
                print(f"网页加载超时，跳过 UID={uid}")
                continue  # 网页加载超时，跳过当前 UID，继续爬取其他数据
            except Exception as e:
                print(f"遇到其他异常，UID={uid}跳过: {str(e)}")
                continue  # 遇到其他异常，跳过当前 UID，继续爬取其他数据

    except WebDriverException as e:
        driver.quit()
        to_excel(filename, all_data)
        print(f"浏览器意外关闭，uid={uid}已被访问: {str(e)}")
    finally:
        driver.quit()
        to_excel(filename, all_data)
        print(f'uid={uid}已被访问')

# 写入excel文件
def to_excel(filename, all_data):
    print(f"Total {len(all_data)} items fetched.")
    df = pd.DataFrame([{
        'ID': relic.id,
        'Name': relic.name,
        'Category': relic.categoryName,
        'Dynasty': relic.dynastyName,
        'Description': relic.description,
        'Image': relic.centerImage
    } for relic in all_data])
    df.to_excel(filename, index=False)
    print(f"Data written to {filename}")

# 异步调用爬虫函数
async def async_craw(f, t, filename):
    driver = start_browser()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, craw, driver, f, t, filename)

# 主函数
def main():
    filename = "relics_taiwan.xlsx"
    tasks = []
    # 这里分成多个任务，并行执行
    tasks.append(async_craw(30070, 30120, filename))
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))

if __name__ == '__main__':
    main()