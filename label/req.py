from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from models import RelicOverview
import pandas as pd
import threading


# 存储爬取的所有文物信息
all_data = []
lock = threading.Lock()

# 创建浏览器实例
def start_browser():
    # 设置Chrome选项以无头模式运行（可选）
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # 确保GUI不出现在前台

    # 指定ChromeDriver的路径（根据你的安装位置调整）
    service = Service("D:\Python39\chromedriver.exe")   

    # 创建一个新的浏览器实例
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# 修改from、to,调整爬取文物范围
def craw(driver,f,t):
    try:
        for i in range(f,t):
            driver.get(f'https://digitalarchive.npm.gov.tw/Antique/Content?uid={i}&Dept=U')

            # 等待特定元素出现，确保页面已经加载完毕
            wait = WebDriverWait(driver, 4)
            tbody_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="collapseExample"]/div/div[1]/table/tbody')))
            #print(tbody_element.text)
            #  提取所需信息 
            tr_elements = tbody_element.find_elements(By.TAG_NAME, "tr")
            image =wait.until(EC.presence_of_element_located((By.CLASS_NAME,'ug-item-wrapper')))#图片链接
            image_url = image.find_element(By.TAG_NAME,'img').get_attribute("src")
            #print(url)
            
            for tr in tr_elements:
                # print(tr.text)
                tds = tr.find_elements(By.TAG_NAME, "td")
                if len(tds) >= 2:
                    label = tds[0].text.strip()
                    value = tds[1].text.strip()
                    print(label, value)
                    if label == '品名':
                        name = value
                        print('品名:', value)
                    elif label == '分類':
                        category = value
                        print('分類:', value)
                    elif label == '說明':
                        description = value
                        print('說明:', value)
                    elif label == '時代':
                        dynasty = value
                        print('時代:', value)
                    
                    if '時代' not in [tr.find_elements(By.TAG_NAME, "td")[0].text.strip() for tr in tr_elements]:
                        dynasty = '' 
                        print('時代:')            
                    # 如果說明不在label中，输出一个空白项
                    if '說明' not in [tr.find_elements(By.TAG_NAME, "td")[0].text.strip() for tr in tr_elements]:
                        description = ''
                        print('說明:')

            # description“说明”赋给RelicOverview.culturalRelicNo
            with lock:
                all_data.append(RelicOverview(name,category,description,dynasty,image_url))

    finally:
       driver.quit()

def to_excel():
    # 处理所有数据
    print(f"Total {len(all_data)} items fetched.")

    # 将数据转换为DataFrame
    df = pd.DataFrame([{
        'Name': relic.name,
        'Category': relic.categoryName,
        'Dynasty': relic.dynastyName,
        'Description': relic.culturalRelicNo,
        'Image': relic.centerImage
    } for relic in all_data])

    # 写入Excel文件
    output_file = './data/relics_taiwan.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Data written to {output_file}")

def multiple_thread():
    #修改fs(from)、ts(to)，调整获取文物url范围
    fs = [30064,30071]
    ts = [30070,30080]
    threads = []
    for f,t in fs,ts:
        threads.append(threading.Thread(target=craw,args=(start_browser(),f,t)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def main():
    multiple_thread()
    to_excel()

if __name__ == '__main__':
    main()


    
