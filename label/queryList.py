import requests
import pandas as pd
from models import RelicOverview
import time
import numpy as np



def fetch_cultural_heritage(page=1):
    url = 'https://digicol.dpm.org.cn/cultural/queryList'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        'page': str(page),
        'keyWord': '',
        'sortType': '',
        'hasImage': 'false',
        'topicId': '',
    }
    response = requests.post(url, headers=headers, data=data)
    # response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching page {page}, status code: {response.status_code}")
        return None



def get_all_tag():
    all_data = []
    page = 1
    while page<=1000:  # 你可以调整这个条件来获取更多页面
        time.sleep(0.1)
        data = fetch_cultural_heritage(page) 
        if data is not None and 'rows' in data and len(data['rows']) > 0:
            for row in data['rows']:
                relic = RelicOverview(row['name'], row['categoryName'], row['culturalRelicNo'], row['dynastyName'],row['centerImage'])
                all_data.append(relic)
            print(f"Fetched page {page} with {len(data['rows'])} items")
            page += 1
        else:
            break

    # 处理所有数据
    print(f"Total {len(all_data)} items fetched.")

    # 将数据转换为DataFrame
    df = pd.DataFrame([{
        'Name': relic.name,
        'Category': relic.categoryName,
        'Number': relic.culturalRelicNo,
        'Dynasty': relic.dynastyName,
        'Image': relic.centerImage
    } for relic in all_data])

    # 写入Excel文件
    output_file = './data/relics_overview1.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Data written to {output_file}")

def toDf_querylist(str1,str2,str3):
     # 将数据转换为DataFrame
    df= pd.DataFrame([{
        "MotifAndPattern" : str1,
        "ObjectType" : str2,
        "FormAndStructure" : str3
    } ])

   
  
