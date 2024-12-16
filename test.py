import requests
from bs4 import BeautifulSoup
import base64
import os

# 外部代理配置
pconfig = {
    'proxyUser': 'wujean_area-MO',
    'proxyPass': 'Wujean1220',
    'proxyHost': 'as.smartproxycn.com',
    'proxyPort': '1000'
}

# 本地代理地址 (Clash 或其他工具)
local_proxy = "http://127.0.0.1:7890"

# 构造 Proxy-Authorization 头
auth = f"{pconfig['proxyUser']}:{pconfig['proxyPass']}"
headers = {
    "Proxy-Authorization": f"Basic {base64.b64encode(auth.encode('utf-8')).decode('utf-8')}"
}

# 代理链配置
proxies = {
    "http": local_proxy,
    "https": local_proxy,
}

# 请求目标地址
url = "https://digitalarchive.npm.gov.tw/Antique/Content?uid=30070&Dept=U"

# 提取内容和图片
try:
    print("发送请求...")
    response = requests.get(url, headers=headers, proxies=proxies, timeout=10)

    # 检查响应
    if response.status_code == 200:
        print("请求成功，解析内容...")
        soup = BeautifulSoup(response.text, 'html.parser')

        # 提取文本信息
        table = soup.find('table')
        if table:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) == 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    print(f"{label}: {value}")
        
        # 提取图片 URL
        img_tag = soup.find('img', class_='ug-thumb-image')  # 根据页面实际结构调整
        if img_tag:
            img_url = img_tag.get('src')
            print(f"图片 URL: {img_url}")

            # 下载图片
            img_response = requests.get(img_url, headers=headers, proxies=proxies, timeout=10)
            if img_response.status_code == 200:
                # 保存图片
                img_filename = os.path.basename(img_url)
                with open(img_filename, 'wb') as f:
                    f.write(img_response.content)
                print(f"图片已保存为: {img_filename}")
            else:
                print(f"图片下载失败，状态码: {img_response.status_code}")
        else:
            print("未找到图片标签。")
    else:
        print(f"请求失败，状态码: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")