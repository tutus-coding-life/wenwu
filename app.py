import gradio as gr
import requests
import cv2
import numpy as np
import json

dify_api_token = "app-eo2OGnlmcVmwdPVuREllSL5d"

def process_input(image_id, artifact_name, category, artist, era, collectionLocation, literatureRecord, symbolism, defaultRequirement, userAlert):
    # 构建一个示例的JSON结构
    inputs = {
        "artifactName": artifact_name,
        "category": category,
        "artist": artist,
        "era": era,
        "collectionLocation": collectionLocation,
        "literatureRecord": literatureRecord,
        "symbolism": symbolism,
        "defaultRequirement":defaultRequirement,
        "userAlert": userAlert
    }
    
    # 获取响应数据
    print(image_id)
    response_data = get_llm_result(image_id, inputs)
    print(response_data)
    res = response_data['data']['outputs']['result']

    # 将响应画在图片上
    # 默认长宽
    # image = np.full((648, 648, 3), dtype=np.uint8)
    # output_image = draw_label_on_image(image, response_data)
    # 返回解析后的数据作为标签
    
    return (
        # output_image,
        res.get('artifact_name', ""),
        res.get('category', ""),
        res.get('artist', ""),
        res.get('era', ""),
        res.get('collectionLocation', ""),
        res.get('literatureRecord', ""),
        res.get('symbolism', ""),
    )

def draw_label_on_image(image_path, response_data):
    # 加载图片
    image = cv2.imread(image_path)
    
    # 获取图像的高度和宽度
    height, width, _ = image.shape
    
    # 解析数据
    artifact_name = response_data.get('artifactName', "")
    category = response_data.get('category', "")
    artist = response_data.get('artist', "")
    era = response_data.get('era', "")
    collection_location = response_data.get('collectionLocation', "")
    literature_record = response_data.get('literatureRecord', "")
    symbolism = response_data.get('symbolism', "")
    
    # 创建标签文本行
    label_lines = [
        f"Name: {artifact_name}",
        f"Category: {category}",
        f"Artist: {artist}",
        f"Era: {era}",
        f"Collection Location: {collection_location}",
        f"Literature Record: {literature_record}",
        f"Symbolism: {symbolism}"
    ]
    
    # 设置字体和大小
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7  # 文字大小适中
    color = (255, 255, 255)  # 白色
    thickness = 2
    
    # 计算文本的尺寸
    text_sizes = [cv2.getTextSize(line, font, font_scale, thickness)[0] for line in label_lines]
    max_width = max([text_size[0] for text_size in text_sizes])
    total_height = sum([text_size[1] for text_size in text_sizes])
    padding = 10  # 文本与边界的距离
    
    # 定义标签的位置（居中对齐）
    x_start = int((width - max_width) / 2)
    y_start = height - int(total_height / 2) - padding * len(label_lines)
    
    # 逐行绘制文本
    y_pos = y_start
    for line in label_lines:
        text_size = cv2.getTextSize(line, font, font_scale, thickness)[0]
        cv2.putText(image, line, (x_start, y_pos), font, font_scale, color, thickness, cv2.LINE_AA)
        y_pos += text_size[1] + padding  # 下一行的位置
    
    return image

def upload_image(image_path):

    base_url = "https://api.dify.ai/v1/files/upload"
    print(image_path)
    # 构造 POST 请求
    headers = {
        'Authorization': f'Bearer {dify_api_token}',
    }
    # 判断是jpg还是png
    if image_path.endswith("jpg"):
        image_type = 'image/jpeg'
    else:
        image_type = 'image/png'
    files = {
        'file': (image_path.split('/')[-1], open(image_path, 'rb'),image_type),  # 明确指定文件类型),
        'user': (None, 'abc-123'),
    }

    response = requests.post(base_url, headers=headers, files=files)

    # 检查响应状态码
    if response.status_code == 201:
        # 假设服务器返回的是 JSON 数据
        try:
            json_response = response.json()
            return json_response.get('id'),"上传成功"
        except ValueError:
            print("Invalid JSON response from server.")
    else:
        print(f"Failed to upload image: {response.status_code}, {response.text}")

    return None,"上传失败"

def get_llm_result(image_id, inputs):
    """
    从 Dify API 获取大模型的结果
    """
    headers = {
        "Authorization": f"Bearer {dify_api_token}"
    }
    req = {
        "inputs": inputs,
        "response_mode": "blocking",
        "user": "abc-123",
        "files": [
            {
                "type": "image",
                # "transfer_method": "local_file",
                "transfer_method": "remote_url",
                # "upload_file_id": image_id
                "url": image_id
            }
        ]
    }
    print(req)
    base_url_workflow = "https://api.dify.ai/v1/workflows/run"

    try:
        response = requests.post(base_url_workflow, headers=headers, json=req)
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                return json_response
            except ValueError:
                print("Invalid JSON response from server.")
        else:
            print(f"Failed to get LLM result: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Request error: {e}")

    return None

# 创建Gradio界面
with gr.Blocks() as demo:
    gr.Markdown("### 文物信息录入系统")

    image_id = gr.Textbox(label="图片ID",visible=True)

    with gr.Row():
        image_input = gr.Image(label="上传文物图片", type="filepath")
        status = gr.Textbox(label="上传状态")

    with gr.Row():
        artifact_name = gr.Textbox(label="文物名称*")
        category = gr.Textbox(label="文物分类*")
        era = gr.Textbox(label="年代*")
        
    with gr.Row():
        artist = gr.Textbox(label="作者（可选）")   
        collectionLocation = gr.Textbox(label="收藏地（可选）")
        
    with gr.Row():
        literatureRecord = gr.Textbox(label="文献记载（可选）", lines=3)
        symbolism = gr.Textbox(label="寓意（可选）", lines=3)
    with gr.Row():
        defaultRequirement = gr.Textbox(label="大模型默认要求（可选）",lines=3)
        userAlert = gr.Textbox(label="发给大模型的描述*",lines=3)
    
    submit_button = gr.Button("提交")
    output_image = gr.Image(type="pil", label="处理后的文物图片",interactive=False)

    image_input.change(
        fn=upload_image,
        inputs=[image_input],
        outputs=[image_id,status]
    )

    submit_button.click(
        fn=process_input,
        inputs=[
            image_id, artifact_name, category, artist, era, collectionLocation, literatureRecord, symbolism, defaultRequirement, userAlert
        ],
        outputs=[
            # output_image,
            artifact_name, category, artist, era, collectionLocation, literatureRecord, symbolism
        ]
    )

# 启动Gradio应用
# demo.launch()
if __name__ == "__main__":
    demo.launch()
    # response_data = {'result': {'artifactName': '五彩瓷瓶', 'category': '瓷器', 'artist': '不详', 'era': '清', 'collectionLocation': '故宫博物院', 'literatureRecord': '不详', 'symbolism': '五彩瓷器的图案多寓意吉祥，如花卉象征富贵，鸟兽代表吉祥，山水寓意长寿。', 'shape': '瓷瓶，瓶身呈扁圆形，顶部有五个小口', 'patternDescription': {'mainPattern': '花卉、鸟兽、山水等图案', 'distinctFeatures': '五彩斑斓，色彩丰富'}, 'color': '五彩', 'material': '瓷器', 'dimensions': '未知', 'origin': '中国', 'restorationRecord': '无记录'}}  
    # response_data = response_data['result']
    # print(json.dumps(response_data, indent=4,ensure_ascii=False))
