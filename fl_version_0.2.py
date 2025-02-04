from flask import Flask, request, render_template_string
import requests
import json
import os

app = Flask(__name__)

HTML = '''
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Chat</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        background-color: #f4f4f9;
        margin: 0;
        padding: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
      }
      .chat-container {
        background-color: #fff;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        width: 80%;
        max-width: 600px;
      }
      .chat-container h1 {
        text-align: center;
        color: #333;
      }
      .chat-container form {
        display: flex;
        margin-bottom: 20px;
      }
      .chat-container input[type="text"] {
        flex: 1;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 16px;
      }
      .chat-container input[type="submit"] {
        padding: 10px 20px;
        border: none;
        border-radius: 4px;
        background-color: #007bff;
        color: #fff;
        font-size: 16px;
        cursor: pointer;
        margin-left: 10px;
      }
      .chat-container input[type="submit"]:hover {
        background-color: #0056b3;
      }
      .chat-container .response {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
        font-size: 16px;
        color: #333;
      }
    </style>
  </head>
  <body>
    <div class="chat-container">
      <h1>Chat</h1>
      <form method="post">
        <input type="text" name="prompt" placeholder="输入你的消息" required>
        <input type="submit" value="发送">
      </form>
      <div class="response">{{ response }}</div>
    </div>
  </body>
</html>
'''

CONVERSATION_FILE = 'conversation.json'

def load_conversation():
    if os.path.exists(CONVERSATION_FILE):
        with open(CONVERSATION_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

def save_conversation(conversation):
    with open(CONVERSATION_FILE, 'w', encoding='utf-8') as file:
        json.dump(conversation, file, ensure_ascii=False, indent=4)

@app.route('/', methods=['GET', 'POST'])
def chat():
    response = ""
    if request.method == 'POST':
        prompt = request.form['prompt']
        conversation = load_conversation()
        conversation.append({"role": "user", "content": prompt})

        # 将对话历史作为上下文发送给模型
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        resp = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'deepseek-r1:1.5b', 'prompt': context, 'stream': False}
        )
        model_response = resp.json()['response']
        conversation.append({"role": "assistant", "content": model_response})
        save_conversation(conversation)

        response = model_response
    return render_template_string(HTML, response=response)

if __name__ == '__main__':
    app.run(port=5000)
