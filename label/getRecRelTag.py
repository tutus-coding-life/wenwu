import requests
import pandas as pd
import time
from models import Tag
import numpy as np
from tqdm import tqdm
def fetch_recommend_tags(code):
    url = 'https://digicol.dpm.org.cn/cultural/getRecRelTag'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'X-Requested-With': 'XMLHttpRequest',
    }
    data = {
    'code': str(code),
    }
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching recommend tags, status code: {response.status_code}")
        return None
    
#对所有文物标签去重
def main():
    type = ["MotifAndPattern","ObjectType","FormAndStructure"]
    df = pd.read_excel('./data/relics_tag.xlsx')
    all_tag = ["MotifAndPattern","ObjectType","FormAndStructure"]
    all_tag0, all_tag1, all_tag2=[], [], []
    for index,row in tqdm(df.iterrows()):
        tag0 = row['MotifAndPattern'].split(',')
        tag1 = row['ObjectType'].split(',')
        tag2 = row['FormAndStructure'].split(',')
        for num in range(2):
            for item in eval(f'tag{num}'):
                if item  not in eval(f'all_tag{num}'):
                    eval(f'all_tag{num}').append(item)
    str1 = ','.join(all_tag0)
    str2 =','.join(all_tag1)
    str3 =','.join(all_tag2)
     # 将数据转换为DataFrame
    df= pd.DataFrame([{
        "MotifAndPattern" : str1,
        "ObjectType" : str2,
        "FormAndStructure" : str3
    } ])
    
    # 写入Excel文件
    output_file = './data/relics_all_tag.xlsx'
    df.to_excel(output_file, index=False)
    print(f"Data written to {output_file}")

#取出单个文物标签
def re():
     #存储三个标签类型
    one_tag = []
    type = ["MotifAndPattern","ObjectType","FormAndStructure"]

    #对excel进行遍历
    num_fetched = 0
    num_not_included = 0
    
    df_querylist = pd.read_excel("./data/relics_overview1.xlsx")

    for index,row in df_querylist.iterrows():
        time.sleep(0.1)
        code = row['Number']
        data = fetch_recommend_tags(code)
        num_fetched +=1

        #处理所有文物标签
        if data['code'] != '000001':
            result = data['result']
            tagSum = ["MotifAndPattern","ObjectType","FormAndStructure"]#增加标签类型在此修改
            index_tagSum = 0
            for tagType in result:#type是result里的每个键值
                if tagType in type :
                    tagStr = ''
                    for item in result[tagType]:#item是字典
                        tagStr = tagStr+ item['tagName'] + ','
                    tagSum[index_tagSum] = tagStr
                    index_tagSum +=1
            tag = Tag(code, tagSum[0], tagSum[1], tagSum[2])
            print(code, tagSum[0], tagSum[1], tagSum[2])
            one_tag.append(tag)
            
        else :
            print(f"result in {code} is None")  
            num_not_included +=1

    # 处理所有数据
    print(f"Total {num_fetched} items'tag fetched.\n{num_not_included} hasn't included")

    # 将数据转换为DataFrame
    df_getRecRelTag = pd.DataFrame([{
        'Number': tag.Number,
        "MotifAndPattern" : tag.MotifAndPattern,
        "ObjectType" : tag.ObjectType,
        "FormAndStructure" : tag.FormAndStructure
    } for tag in one_tag])
    
    # 写入Excel文件
    output_file = './data/relics_tag.xlsx'
    df_getRecRelTag.to_excel(output_file, index=False)
    print(f"Data written to {output_file}")


        
          

  
if __name__ == '__main__':
    main()