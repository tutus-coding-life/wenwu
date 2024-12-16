import asyncio
import base64
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
from tqdm import tqdm


# 配置本地代理和外部代理
LOCAL_PROXY = "http://127.0.0.1:7890"  # 本地代理地址（Clash 等工具）
pconfig={
    'proxyUser':'wujean',
    'proxyPass':'Wujean1220',
    'proxyHost':'proxy.smartproxycn.com',
    'proxyPort':'1000'
}

# 构造外部代理认证信息
auth = f"{pconfig['proxyUser']}:{pconfig['proxyPass']}"
encoded_auth = base64.b64encode(auth.encode('utf-8')).decode('utf-8')
headers = {
    "Proxy-Authorization": f"Basic {encoded_auth}"
}


# 文物信息数据类
class RelicOverviewTaiwan:
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


# 配置浏览器实例，并设置本地代理
def start_browser_with_local_proxy_and_headers():
    """
    配置浏览器使用本地代理，并在请求头中添加外部代理认证信息。
    """
    chrome_options = Options()
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(f'--proxy-server={LOCAL_PROXY}')  # 配置本地代理

    # 添加请求头，注入外部代理认证信息
    chrome_options.add_argument(f'--header="Proxy-Authorization: {headers["Proxy-Authorization"]}"')

    service = Service("./chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# 爬取数据
def craw(driver, f, t):
    uid = -1
    all_data = []
    try:
        for i in tqdm(range(f, t)):
            uid = i
            driver.get(f'https://digitalarchive.npm.gov.tw/Antique/Content?uid={i}&Dept=U')
            try:
                # 等待页面加载完成
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
                dynasty = dynasty if dynasty else ''
                description = description if description else ''

                # 将文物信息添加到 all_data 列表
                all_data.append(RelicOverviewTaiwan(i, name, category, '', dynasty, image_url, description))
                time.sleep(1)  # 设置请求间隔，防止被限制

            except TimeoutException:
                print(f"网页加载超时，跳过 UID={uid}")
                continue
            except Exception as e:
                print(f"遇到异常，UID={uid} 跳过: {str(e)}")
                continue

    except WebDriverException as e:
        print(f"浏览器异常关闭，UID={uid} 已被访问: {str(e)}")
    finally:
        driver.quit()
        return all_data


# 写入 Excel 文件
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


# 异步爬虫
async def async_craw(f, t):
    print(f"当前代理链: 本地代理 {LOCAL_PROXY} -> 外部代理 {pconfig['proxyHost']}:{pconfig['proxyPort']}")
    driver = start_browser_with_local_proxy_and_headers()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, craw, driver, f, t)


# 主函数
async def main():
    filename = "relics_taiwan.xlsx"
    tasks = []
    range_start = 30070
    range_end = 30120
    step = 20  # 每次爬取的步长

    # 创建多个任务，每次爬取 step 个
    for i in range(range_start, range_end, step):
        tasks.append(async_craw(i, min(i + step, range_end)))

    # 等待所有任务完成
    results = await asyncio.gather(*tasks)

    # 合并所有批次结果
    all_data = [item for batch in results for item in batch]

    # 写入 Excel
    to_excel(filename, all_data)


if __name__ == '__main__':
    asyncio.run(main())