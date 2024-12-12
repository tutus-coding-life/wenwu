import gradio as gr
import requests
import cv2
import numpy as np
import json

dify_api_token = "app-QFRRLvDLiDvF82tuF6SUEzIj"

def process_input(Name,Category,Dynasty,Image_url,Describe):
    # 构建一个示例的JSON结构
    inputs = {
        "Name": Name,
        "Category": Category,
        "Dynasty": Dynasty,
        "Image_url": Image_url,
        "Describe": Describe
    }

    return inputs

def upload_file(file_path, user_id="abc-123", api_key="app-QFRRLvDLiDvF82tuF6SUEzIj", url="http://192.168.11.127/v1/files/upload"):
    """
    上传文件或处理远程 URL。

    Args:
        file_path_or_url (str): 本地文件路径或远程 URL。
        user_id (str): 用户标识，用于定义终端用户的身份。
        api_key (str): API 密钥。
        url (str): 文件上传的接口地址。

    Returns:
        image_id: 上传成功时返回图片的id或url
        None: 上传失败时返回 None。
    """
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
    #     # 处理远程 URL 文件
    #     print("检测到远程 URL，不执行上传操作。")
    #     return {"url": file_path_or_url, "info": "文件是远程URL，未上传"}

    # else:
    # 本地文件上传
    try:
        # 检测文件类型
        if file_path.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
            mime_type = "image/" + file_path.split('.')[-1]
        else:
            # return {"error": "不支持的文件类型，只支持图片格式。"}
            return None

        # 准备文件数据
        files = {
            "file": (file_path.split('/')[-1], open(file_path, 'rb'), mime_type),
            "user": (None, user_id),
        }

        response = requests.post(url, headers=headers, files=files)

        if response.status_code == 201:
            return response.json()['id']  # 成功返回服务器响应
        else:
            print(f"文件上传失败: {response.status_code}")
            print(response.text)
            return None
    except FileNotFoundError:
        print("文件未找到，请检查路径是否正确。")
        return None
    except Exception as e:
        print(f"请求出错: {e}")
        return None

def get_llm_result(api_key, inputs, user_id, image_url=None, upload_file_id=None, response_mode="blocking", workflow_url="http://192.168.11.127/v1/workflows/run"):
    """
    从 Dify API 获取大模型的结果。

    Args:
        api_key (str): API 密钥。
        inputs (dict): Workflow 所需的输入变量。
        user_id (str): 用户标识，用于定义终端用户的身份。
        image_url (str, optional): 远程图片地址（当传递方式为 remote_url 时）。
        upload_file_id (str, optional): 本地上传的文件 ID（当传递方式为 local_file 时）。
        response_mode (str, optional): 返回响应模式，支持 "blocking"（默认）和 "streaming"。
        workflow_url (str, optional): Workflow 执行的 API URL。

    Returns:
        dict or None: 执行成功时返回服务器的 JSON 响应；失败时返回 None。
    """

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    # 构建请求体
    req = {
        "inputs": inputs,
        "response_mode": response_mode,
        "user": user_id,
        "files": []
    }

    # 添加文件部分
    if image_url:
        req["files"].append({
            "type": "image",
            "transfer_method": "remote_url",
            "url": image_url
        })
    elif upload_file_id:
        req["files"].append({
            "type": "image",
            "transfer_method": "local_file",
            "upload_file_id": upload_file_id
        })

    # 发送请求
    try:
        response = requests.post(workflow_url, headers=headers, json=req)
        
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

def upload_image_and_get_id(image_path=None, image_url=None):
    """
    上传图片并返回文件 ID 或 URL。
    """
    if image_url:  # 远程 URL
        return image_url, "图片 URL 已指定"
    elif image_path:  # 本地文件
        file_id = upload_file(image_path,url="http://192.168.11.127/v1/files/upload")
        if file_id:
            return file_id, "上传成功"
        else:
            return None, "上传失败"

def process_and_get_result(image_identifier, name, category, dynasty, describe, upload_type):
    """
    将用户输入发送给大模型处理，并返回结果。
    """
    if not image_identifier:
        return "请先上传图片或指定图片 URL！", None

    inputs = {
        "Name": name,
        "Category": category,
        "Dynasty": dynasty,
        # "Image" if upload_type == "url" else "Image": image_identifier,
        "Describe": describe
    }

    result = get_llm_result(
        api_key=dify_api_token,
        inputs=inputs,
        user_id="abc-123",
        image_url=image_identifier if upload_type == "url" else None,
        upload_file_id=image_identifier if upload_type == "local_file" else None,
        workflow_url="http://192.168.11.127/v1/workflows/run",
    )
    print(result)
    result = result["data"]['outputs']
    if result:
        if "text" in result and "data" in result["text"]:
            res = result["text"]["data"]
            # 返回从json中提取的信息
            Name =  res.get("Name", "未知")
            Category = res.get("Category", "未知")
            Dynasty = res.get("Dynasty", "未知")
            Describe = res.get("Describe", "未知")
            MotifAndPattern = {"图案与纹样":res.get("MotifAndPattern", "未知")}
            FormAndStructure = {"形制结构":res.get("FormAndStructure", "未知")}
            MotifAndPattern = show_tags(MotifAndPattern)
            FormAndStructure = show_tags(FormAndStructure)
            return "处理成功",Name, Category, Dynasty, Describe, MotifAndPattern, FormAndStructure
        else:
            return "处理失败，请检查大模型返回内容。", None, None, None, None, None, None
    else:
        return "处理失败，请稍后重试。", None, None, None, None, None, None
    
def show_tags(tag_groups):
    """
    根据标签组生成 HTML 内容，用于展示标签云。

    :param tag_groups: dict 格式的标签组，每个 key 是分类名称，value 是对应标签列表。
    :return: 返回生成的 HTML 字符串。
    """
    import random

    # 标签框的随机颜色
    colors = ["#ff4d4d", "#4caf50", "#2196f3", "#ff9800"]  # 红、绿、蓝、橙

    # 生成每个分类的 HTML
    group_html = ""
    for category, tags in tag_groups.items():
        tag_html = "".join(
            f'<a class="tag" style="background-color: {random.choice(colors)};">{tag}</a>'
            for tag in tags
        )
        group_html += f"""
        <section>
            <h2>{category}</h2>
            <div class="tag-cloud">
                {tag_html}
            </div>
        </section>
        """

    # 总的 HTML 模板
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #000; /* 黑色背景 */
                color: #ccc; /* 灰色文字 */
            }}
            header {{
                background-color: #333;
                color: white;
                text-align: center;
                padding: 1em 0;
            }}
            .container {{
                width: 80%;
                margin: 20px auto;
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: flex-start;
            }}
            section {{
                background-color: #222; /* 深灰色背景 */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
                border-radius: 8px;
                padding: 20px;
                width: 100%;
                max-width: 600px;
                text-align: left;
                color: #ccc; /* 灰色文字 */
            }}
            section h2 {{
                font-size: 20px;
                margin-bottom: 10px;
                color: #fff; /* 白色标题 */
            }}
            .tag-cloud {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                justify-content: flex-start; /* 左对齐 */
            }}
            .tag {{
                color: white; /* 标签文字颜色 */
                padding: 5px 10px;
                border-radius: 5px;
                text-decoration: none;
                font-size: 16px;
                transition: background-color 0.3s;
            }}
            .tag:hover {{
                filter: brightness(1.2); /* 增加亮度 */
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {group_html}
        </div>
    </body>
    </html>
    """

def process_and_get_result_mock(image_identifier, name, category, dynasty, describe, upload_type):
    """
    模拟处理用户输入并返回结果。
    """
    data = {'Name': '斗彩龙纹碗', 'Dynasty': '清康熙', 'Category': '瓷碗', 'MotifAndPattern': ['龙纹', '花卉纹', '描绘生物的图案与纹样'], 'FormAndStructure': ['撇口', '圈足'], 'Describe': '此碗以斗彩技法绘制，碗身饰有生动的龙纹和花卉纹，造型端庄，工艺精湛，体现了清康熙时期瓷器的高超技艺。'}
    return "处理成功", data['Name'], data['Category'], data['Dynasty'], data['Describe'], show_tags({"图案与纹样": data['MotifAndPattern']}), show_tags({"形制结构": data['FormAndStructure']})
    
# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("### 文物信息录入系统")

    with gr.Row():
        upload_type = gr.Radio([
            "url",
            "local_file"
        ], value="url", label="选择上传方式",)
        image_input = gr.Image(label="上传本地图片", type="filepath", visible=False)
        image_url_input = gr.Textbox(label="图片 URL", visible=True)
        upload_status = gr.Textbox(label="上传状态", interactive=False)
        image_identifier = gr.Textbox(label="图片标识", interactive=False, visible=False)

    with gr.Row():
        artifact_name = gr.Textbox(label="文物名称*", placeholder="请输入文物名称")
        category = gr.Textbox(label="文物分类*", placeholder="请输入文物分类")
        dynasty = gr.Textbox(label="年代*", placeholder="请输入文物年代")
    describe = gr.Textbox(label="描述*", lines=3, placeholder="请输入描述")

    submit_button = gr.Button("提交")
    result_status = gr.Textbox(label="处理状态", interactive=False,visible=False)
    with gr.Row():
        MotifAndPattern_tags = gr.HTML(label="文物标签")
        FormAndStructure_tags = gr.HTML(label="文物标签")

    # 动态切换输入方式
    def toggle_input(upload_type):
        return gr.update(visible=(upload_type == "local_file")), gr.update(visible=(upload_type == "url"))

    upload_type.change(
        fn=toggle_input,
        inputs=[upload_type],
        outputs=[image_input, image_url_input]
    )

    # 上传图片
    image_input.change(
        fn=upload_image_and_get_id,
        inputs=[image_input, image_url_input],
        outputs=[image_identifier, upload_status]
    )
    image_url_input.change(
        fn=upload_image_and_get_id,
        inputs=[image_input, image_url_input],
        outputs=[image_identifier, upload_status]
    )

    # 提交并获取结果
    submit_button.click(
        # fn=process_and_get_result,
        fn=process_and_get_result_mock,
        inputs=[
            image_identifier, artifact_name, category, dynasty, describe, upload_type
        ],
        outputs=[result_status, artifact_name, category, dynasty, describe,MotifAndPattern_tags, FormAndStructure_tags]
    )

# 启动 Gradio 应用
if __name__ == "__main__":
    demo.launch()