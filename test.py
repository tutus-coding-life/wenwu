import requests

url = 'https://api.dify.ai/v1/files/upload'
headers = {
    'Authorization': 'Bearer app-eo2OGnlmcVmwdPVuREllSL5d',
}

file_path = "/Users/wujean/Downloads/533.jpg"  # 文件路径
user_id = "abc-123"  # 用户ID

files = {
    'file': ('533.jpg', open(file_path, 'rb'), 'image/jpeg'),  # 明确指定文件类型
    'user': (None, user_id),
}

response = requests.post(url, headers=headers, files=files)

# 打印响应内容
print(response.status_code)
print(response.text)