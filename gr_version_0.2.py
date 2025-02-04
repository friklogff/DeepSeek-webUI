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


# 上传文件并分析
def upload_and_analyze(file, message, chat_history):
    if file is None:
        return "⚠️ 未选择文件", chat_history

    try:
        with open(file.name, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except Exception as e:
        return f"⚠️ 读取文件失败：{str(e)}", chat_history

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
        ai_response = f"⚠️ 请求出错: {str(e)}"

    conversation.append({"role": "assistant", "content": ai_response})
    save_conversation(conversation)

    chat_history.append((message, ai_response))
    return "✅ 文件已上传并分析完成", chat_history


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
        ai_response = f"⚠️ 请求出错: {str(e)}"

    conversation.append({"role": "assistant", "content": ai_response})
    save_conversation(conversation)

    chat_history.append((message, ai_response))
    return "", chat_history


# 自定义 CSS 样式
custom_css = """
#chatbot {
    height: 65vh !important;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    background: linear-gradient(145deg, #f8f9fa 0%, #ffffff 100%);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.message-user {
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
    color: white !important;
    border-radius: 15px 15px 3px 15px !important;
    margin: 8px 0 !important;
    padding: 12px 18px !important;
    max-width: 85% !important;
    margin-left: auto !important;
}

.message-user::before {
    content: "👤";
    margin-right: 8px;
    filter: drop-shadow(0 1px 1px rgba(0,0,0,0.1));
}

.message-assistant {
    background: linear-gradient(135deg, #f3f4f6 0%, #f9fafb 100%) !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 15px 15px 15px 3px !important;
    margin: 8px 0 !important;
    padding: 12px 18px !important;
    max-width: 85% !important;
}

.message-assistant::before {
    content: "🤖";
    margin-right: 8px;
    filter: drop-shadow(0 1px 1px rgba(0,0,0,0.1));
}

.upload-success {
    color: #10b981 !important;
    font-weight: 500;
    padding-left: 5px;
}

.upload-success::before {
    content: "✅ ";
}

.error-message::before {
    content: "⚠️ ";
}

.file-upload {
    border: 2px dashed #e5e7eb !important;
    border-radius: 12px !important;
    padding: 20px !important;
    background: #f9fafb !important;
}

.gradio-container {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%) !important;
}

.input-box {
    border: 2px solid #e5e7eb !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
}

.input-box:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
}

.send-btn {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
}

.send-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.3);
}

.footer {
    text-align: center;
    padding: 15px;
    color: #6b7280;
    border-top: 1px solid #e5e7eb;
    margin-top: 20px;
}
"""

# 主题配置
theme = gr.themes.Base(
    primary_hue="blue",
    secondary_hue="green",
    font=[gr.themes.GoogleFont("Inter"), "Arial", "sans-serif"]
).set(
    button_primary_background_fill="linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)",
    button_primary_border_color="#2563eb",
    button_primary_text_color="#ffffff",
    border_color_primary="#e5e7eb",
    link_text_color="#3b82f6",
)

with gr.Blocks(css=custom_css, theme=theme) as demo:
    gr.Markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="font-size: 2.5rem; margin: 0; 
                   background: linear-gradient(45deg, #3b82f6, #10b981);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;">
            🚀 AI 智能助手
        </h1>
        <p style="color: #6b7280; margin-top: 8px;">📤 上传文件或直接提问获取帮助 💡</p>
    </div>
    """)

    with gr.Row():
        file_upload = gr.File(
            label="📁 上传文档（支持 TXT/PDF/DOCX）",
            file_types=[".txt", ".pdf", ".docx"],
            elem_classes="file-upload",
            # info="📌 请上传需要分析的文件"
        )

    chatbot = gr.Chatbot(
        elem_id="chatbot",
        bubble_full_width=False,
        show_label=False,
        avatar_images=(
            "https://i.imgur.com/7OaW6oX.png",  # 用户头像
            "https://i.imgur.com/qjLdQJ0.png"  # AI头像
        )
    )

    with gr.Row():
        msg = gr.Textbox(
            scale=5,
            placeholder="💬 输入您的问题...",
            container=False,
            autofocus=True,
            elem_classes="input-box",
            label=""
        )
        submit_btn = gr.Button(
            "📤 发送消息 →",
            elem_classes="send-btn",
            scale=1
        )

    # 交互逻辑
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

    file_upload.upload(
        fn=upload_and_analyze,
        inputs=[file_upload, msg, chatbot],
        outputs=[gr.Textbox(label="📤 上传结果", elem_classes="upload-success"), chatbot]
    )

    submit_btn.click(
        fn=chat_with_ai,
        inputs=[msg, chatbot],
        outputs=[msg, chatbot]
    )

    # 底部提示
    gr.Markdown("""
    <div class="footer">
        🛠️ 功能提示：
        <span style="margin: 0 10px;">• ✨ 支持多轮对话</span>
        <span style="margin: 0 10px;">• 📚 文件内容分析</span>
        <span style="margin: 0 10px;">• ⚡ 实时响应</span>
    </div>
    """)

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