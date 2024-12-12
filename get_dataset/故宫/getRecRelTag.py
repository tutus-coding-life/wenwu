import requests
import pandas as pd
import time
from models import Tag
from tqdm import tqdm

# ========== 工具函数 ==========

def fetch_recommend_tags(code):
    """
    根据文物编号从API获取推荐标签
    :param code: 文物编号
    :return: 返回包含推荐标签的JSON数据，如果请求失败返回None
    """
    url = 'https://digicol.dpm.org.cn/cultural/getRecRelTag'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = {'code': str(code)}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching recommend tags, status code: {response.status_code}")
        return None

def save_to_excel(data, output_file):
    """
    将数据保存到Excel文件
    :param data: DataFrame数据
    :param output_file: 输出文件路径
    """
    data.to_excel(output_file, index=False)
    print(f"Data written to {output_file}")

def deduplicate_tags(df, columns):
    """
    对指定列中的标签去重并返回合并后的字符串
    :param df: 包含标签的DataFrame
    :param columns: 需要处理的列名列表
    :return: 每列合并后的标签字符串
    """
    deduplicated_tags = []
    for col in columns:
        tags = set()
        for row in df[col].dropna():
            tags.update(row.split(','))
        deduplicated_tags.append(','.join(tags))
    return deduplicated_tags

# ========== 主功能函数 ==========

def process_all_tags(input_file, output_file):
    """
    对所有文物标签去重，并保存到Excel文件
    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    """
    df = pd.read_excel(input_file)
    tag_columns = ["MotifAndPattern", "ObjectType", "FormAndStructure"]
    combined_tags = deduplicate_tags(df, tag_columns)

    # 构造新的DataFrame保存结果
    result_df = pd.DataFrame([{
        "MotifAndPattern": combined_tags[0],
        "ObjectType": combined_tags[1],
        "FormAndStructure": combined_tags[2]
    }])
    save_to_excel(result_df, output_file)

def fetch_and_save_tags(input_file, output_file):
    """
    根据文物编号从API获取标签，并保存到Excel文件
    :param input_file: 包含文物编号的输入文件路径
    :param output_file: 输出文件路径
    """
    df_querylist = pd.read_excel(input_file)
    tags_data = []
    type_keys = ["MotifAndPattern", "ObjectType", "FormAndStructure"]

    num_fetched = 0
    num_not_included = 0

    for index, row in tqdm(df_querylist.iterrows(), total=len(df_querylist)):
        time.sleep(0.1)
        code = row['Number']
        data = fetch_recommend_tags(code)
        num_fetched += 1

        if data and data.get('code') != '000001':
            result = data.get('result', {})
            tag_values = []
            for key in type_keys:
                tag_values.append(','.join([item['tagName'] for item in result.get(key, [])]))
            tags_data.append({
                'Number': code,
                "MotifAndPattern": tag_values[0],
                "ObjectType": tag_values[1],
                "FormAndStructure": tag_values[2]
            })
        else:
            print(f"Result for {code} is None")
            num_not_included += 1

    print(f"Total {num_fetched} items' tags fetched. {num_not_included} items not included.")

    # 保存到Excel
    result_df = pd.DataFrame(tags_data)
    save_to_excel(result_df, output_file)

# ========== 主程序入口 ==========

if __name__ == '__main__':
    # 去重处理并保存到文件
    process_all_tags('./data/relics_tag.xlsx', './data/relics_all_tag.xlsx')

    # 从API获取标签并保存到文件
    fetch_and_save_tags('./data/relics_overview1.xlsx', './data/relics_tag.xlsx')