import gradio as gr

def display_tags():
    tags = ["缠枝纹", "龙穿花", "凤穿花", "龙凤", "植物纹样", "花卉纹"]
    tag_html = "".join(f'<div class="tag">{tag}</div>' for tag in tags)
    return f"""
    <style>
        .tags-container {{
            display: flex;
            gap: 10px;
            justify-content: center;
            align-items: center;
        }}
        .tag {{
            background-color: #f0f0f0;
            border-radius: 50%;
            padding: 10px 20px;
            text-align: center;
            font-size: 16px;
            color: #333;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }}
    </style>
    <div class="tags-container">
        {tag_html}
    </div>
    """

iface = gr.Interface(
    fn=display_tags,
    inputs=None,
    outputs=gr.HTML(),
    title="可选标签集合",
    description="选择以下标签："
)

iface.launch()