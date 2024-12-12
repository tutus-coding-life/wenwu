import requests
import pandas as pd
from models import RelicOverview
import time

# ========== 工具函数 ==========

def fetch_cultural_heritage(page=1):
    """
    按页获取故宫文物的列表
    :param page: 页码
    :return: 包含文物列表的JSON数据，如果请求失败返回None
    """
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
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching page {page}, status code: {response.status_code}")
        return None

def save_to_excel(data, output_file):
    """
    将数据保存到Excel文件
    :param data: DataFrame数据
    :param output_file: 输出文件路径
    """
    data.to_excel(output_file, index=False)
    print(f"Data written to {output_file}")

# ========== 主功能函数 ==========

def get_all_relic_overview(target_page):
    """
    获取指定页数的所有文物概览信息并保存到Excel
    :param target_page: 需要获取的页数
    """
    all_data = []
    page = 1
    while page <= target_page:
        time.sleep(0.1)  # 控制请求频率
        data = fetch_cultural_heritage(page)
        if data is not None and 'rows' in data and len(data['rows']) > 0:
            for row in data['rows']:
                # 创建 RelicOverview 对象并存储到列表
                relic = RelicOverview(
                    row['name'],
                    row['categoryName'],
                    row['culturalRelicNo'],
                    row['dynastyName'],
                    row['centerImage']
                )
                all_data.append(relic)
            print(f"Fetched page {page} with {len(data['rows'])} items.")
            page += 1
        else:
            break

    print(f"Total {len(all_data)} items fetched.")

    # 将文物数据转换为DataFrame
    df = pd.DataFrame([{
        'Name': relic.name,
        'Category': relic.categoryName,
        'Number': relic.culturalRelicNo,
        'Dynasty': relic.dynastyName,
        'Image': relic.centerImage
    } for relic in all_data])

    # 保存到Excel
    output_file = './data/dataset/故宫/relics_overview.xlsx'
    save_to_excel(df, output_file)

def create_tag_dataframe(motif_and_pattern, object_type, form_and_structure):
    """
    创建包含标签的DataFrame
    :param motif_and_pattern: 纹样与图案标签
    :param object_type: 器物类型标签
    :param form_and_structure: 形制与结构标签
    :return: 包含标签的DataFrame
    """
    return pd.DataFrame([{
        "MotifAndPattern": motif_and_pattern,
        "ObjectType": object_type,
        "FormAndStructure": form_and_structure
    }])

# ========== 主程序入口 ==========

if __name__ == '__main__':
    # 获取故宫文物概览并保存
    target_page = 5  # 修改为实际需要的页数
    get_all_relic_overview(target_page)

    # 示例：创建标签DataFrame
    df_tags = create_tag_dataframe("花纹,图案", "青铜器", "对称结构")
    save_to_excel(df_tags, './data/dataset/故宫/relics_tags_example.xlsx')