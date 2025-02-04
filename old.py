import gradio as gr
import requests
import json
from typing import Iterator, List

# 自定义颜色主题
theme = gr.themes.Default(
    primary_hue="emerald",  # 主色调为绿色
    secondary_hue="teal",  # 次级色调为蓝绿色
    font=[gr.themes.GoogleFont("Noto Sans SC"), "Arial", "sans-serif"]  # 使用中文字体
).set(
    button_primary_background_fill="*primary_500",  # 按钮背景颜色
    button_primary_background_fill_hover="*primary_600",  # 按钮悬停时的背景颜色
)

# 流式响应生成函数
def stream_response(prompt: str, history: List[List[str]], temperature: float, max_tokens: int) -> Iterator[List[List[str]]]:
    """流式响应生成函数，逐步生成模型的回复"""
    messages = [{"role": "user", "content": prompt}]
    response = requests.post(
        'http://localhost:11434/api/chat',
        json={
            'model': 'deepseek-r1:1.5b',
            'messages': messages,
            'stream': True,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens
            }
        },
        stream=True
    )
    partial_response = ""
    for chunk in response.iter_lines():
        if chunk:
            data = json.loads(chunk.decode("utf-8"))
            if "message" in data and "content" in data["message"]:
                partial_response += data["message"]["content"]
                # 返回符合 Chatbot 组件要求的格式
                yield history + [[prompt, partial_response]]

# 创建 Gradio 界面
def create_ui():
    with gr.Blocks(theme=theme, title="DeepSeek 智能助手", css=".gradio-container {max-width: 800px !important}") as demo:
        # 页头
        gr.Markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="margin: 0; color: #2d3748;">🎯 DeepSeek 智能助手</h1>
            <p style="color: #718096;">基于 deepseek-r1:1.5b 模型的本地部署版本</p>
        </div>
        """)
        # 主界面布局
        with gr.Row():
            # 左侧聊天区
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="对话记录",
                    height=500,
                    bubble_full_width=False,
                    avatar_images=("user.png", "bot.png")  # 用户和机器人的头像
                )
                input_txt = gr.Textbox(
                    placeholder="输入您的问题...",
                    label=" ",
                    container=False,
                    autofocus=True
                )
                with gr.Row():
                    submit_btn = gr.Button("发送", variant="primary")
                    clear_btn = gr.ClearButton([input_txt, chatbot], value="清空对话")
            # 右侧控制面板
            with gr.Column(scale=1):
                gr.Markdown("**⚙️ 参数设置**")
                temperature = gr.Slider(
                    minimum=0.1,
                    maximum=1.0,
                    value=0.7,
                    step=0.1,
                    label="创造力",
                    info="值越大回答越随机"
                )
                max_tokens = gr.Slider(
                    minimum=100,
                    maximum=4096,
                    value=2048,
                    step=100,
                    label="最大长度",
                    info="限制生成内容长度"
                )
                gr.Markdown("---")
                gr.Markdown("**📝 系统提示词**")
                system_prompt = gr.Textbox(
                    placeholder="(可选) 系统级提示词",
                    lines=3,
                    max_lines=5
                )
        # 交互逻辑
        input_msg = input_txt.submit(
            fn=stream_response,
            inputs=[input_txt, chatbot, temperature, max_tokens],
            outputs=[chatbot],
            show_progress="hidden"
        ).then(lambda: "", None, input_txt)
        submit_btn.click(
            fn=stream_response,
            inputs=[input_txt, chatbot, temperature, max_tokens],
            outputs=[chatbot],
            show_progress="hidden"
        ).then(lambda: "", None, input_txt)
    return demo

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(favicon_path="icon.png", show_error=True)