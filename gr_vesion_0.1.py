import gradio as gr
import requests
import json
import os

CONVERSATION_FILE = 'conversation.json'

# 加载对话历史
def load_conversation():
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# 保存对话历史
def save_conversation(conversation):
    with open(CONVERSATION_FILE, 'w', encoding='utf-8') as file:
        json.dump(conversation, file, ensure_ascii=False, indent=4)

# 上传文件并传递给 Ollama API
def upload_and_analyze(file, message, chat_history):
    if file is None:
        return "未选择文件", chat_history

    # 读取文件内容
    try:
        with open(file.name, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        return f"读取文件失败：{str(e)}", chat_history

    # 将文件内容作为上下文传递给 Ollama API
    conversation = load_conversation()
    conversation.append({"role": "user", "content": message + "\n\n" + file_content})

    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'deepseek-r1:1.5b', 'prompt': context, 'stream': False}
        )
        response.raise_for_status()
        ai_response = response.json()['response']
    except Exception as e:
        ai_response = f"请求出错: {str(e)}"

    conversation.append({"role": "assistant", "content": ai_response})
    save_conversation(conversation)

    chat_history.append((message, ai_response))
    return f"文件已上传并分析完成", chat_history

# 聊天功能
def chat_with_ai(message, chat_history):
    conversation = load_conversation()
    conversation.append({"role": "user", "content": message})

    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])

    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'deepseek-r1:1.5b', 'prompt': context, 'stream': False}
        )
        response.raise_for_status()
        ai_response = response.json()['response']
    except Exception as e:
        ai_response = f"请求出错: {str(e)}"

    conversation.append({"role": "assistant", "content": ai_response})
    save_conversation(conversation)

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

    # 文件上传组件
    file_upload = gr.File(label="上传文件")

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

    # 文件上传并分析
    file_upload.upload(
        fn=upload_and_analyze,
        inputs=[file_upload, msg, chatbot],
        outputs=[gr.Textbox(label="上传结果"), chatbot]
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