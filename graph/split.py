import pandas as pd
import csv
import os

def split_file(file_path):
    """
    将Excel文件中的数据拆分成多个CSV文件。
    每个CSV文件分别存储文物的信息、纹样、器型和形式与结构。
    
    Args:
        file_path (str): 输入Excel文件的路径。

    Outputs:
        生成多个CSV文件，存储在输入文件所在目录。
    """
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    # 生成输出文件名，基于输入文件名
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    artifact_file = f"{base_name}_artifacts.csv"
    motifs_file = f"{base_name}_motifs.csv"
    object_types_file = f"{base_name}_object_types.csv"
    form_and_structure_file = f"{base_name}_form_and_structure.csv"

    def process_row(row):
        """
        处理每一行数据并写入对应的CSV文件。
        
        Args:
            row (pd.Series): 数据表中的一行。
        """
        # 提取文物的基本信息
        artifact = {
            "Name": row['Name'],
            "Category": row['Category'],
            "Dynasty": row['Dynasty'],
            "Image": row['Image']
        }

        # 将多值字段分割成列表
        motifs = row['MotifAndPattern'].strip(',').split(',') if pd.notna(row['MotifAndPattern']) else []
        object_types = row['ObjectType'].strip(',').split(',') if pd.notna(row['ObjectType']) else []
        form_and_structure = row['FormAndStructure'].strip(',').split(',') if pd.notna(row['FormAndStructure']) else []

        # 写入 artifacts.csv
        with open(artifact_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["Name", "Category", "Dynasty", "Image"])
            if file.tell() == 0:  # 如果文件为空，则写入表头
                writer.writeheader()
            writer.writerow(artifact)

        # 写入 motifs.csv
        with open(motifs_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # 如果文件为空，则写入表头
                writer.writerow(["Artifact_Name", "Motif"])
            for motif in motifs:
                writer.writerow([artifact["Name"], motif])

        # 写入 object_types.csv
        with open(object_types_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # 如果文件为空，则写入表头
                writer.writerow(["Artifact_Name", "Object_Type"])
            for object_type in object_types:
                writer.writerow([artifact["Name"], object_type])

        # 写入 form_and_structure.csv
        with open(form_and_structure_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # 如果文件为空，则写入表头
                writer.writerow(["Artifact_Name", "Form"])
            for form in form_and_structure:
                writer.writerow([artifact["Name"], form])

    # 遍历DataFrame中的每一行，调用处理函数
    for _, row in df.iterrows():
        process_row(row)

    print("CSV文件已成功生成。")

# 示例调用
# split_file("path_to_your_file.xlsx")