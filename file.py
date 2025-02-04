import gradio as gr
import requests
import json
import os

CONVERSATION_FILE = 'conversation.json'


def load_conversation():
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []


def save_conversation(conversation):
    with open(CONVERSATION_FILE, 'w', encoding='utf-8') as file:
        json.dump(conversation, file, ensure_ascii=False, indent=4)


def chat_with_ai(message, chat_history):
    # 加载对话历史
    conversation = load_conversation()

    # 添加用户消息
    conversation.append({"role": "user", "content": message})

    # 构造上下文
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])

    # 调用 Ollama API
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'deepseek-r1:1.5b', 'prompt': context, 'stream': False}
        )
        response.raise_for_status()
        ai_response = response.json()['response']
    except Exception as e:
        ai_response = f"请求出错: {str(e)}"

    # 添加 AI 回复并保存
    conversation.append({"role": "assistant", "content": ai_response})
    save_conversation(conversation)

    # 更新聊天历史（用于 Gradio 显示）
    chat_history.append((message, ai_response))

    return "", chat_history


# 自定义 CSS
custom_css = """
#chatbot {
    height: 60vh !important;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 15px;
}
footer {
    visibility: hidden
}
"""

with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Chat with AI")

    # 聊天记录显示
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        bubble_full_width=False,
        show_label=False
    )

    # 输入区域
    with gr.Row():
        msg = gr.Textbox(
            scale=4,
            placeholder="输入你的消息...",
            container=False,
            autofocus=True
        )
        submit_btn = gr.Button("发送", scale=1)

    # 清除输入框
    msg.submit(
        fn=lambda x: ("",),
        inputs=msg,
        outputs=msg,
        queue=False
    ).then(
        fn=chat_with_ai,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

    submit_btn.click(
        fn=chat_with_ai,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

if __name__ == "__main__":
    # 初始化对话文件
    if not os.path.exists(CONVERSATION_FILE):
        save_conversation([])

    demo.launch(
        server_port=5000,
        show_error=True,
        favicon_path=None,
        share=False
    )