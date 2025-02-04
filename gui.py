from flask import Flask, request, render_template_string, jsonify
import os
import json

app = Flask(__name__)

# 历史记录文件夹路径
HISTORY_DIR = 'history'

# 获取历史记录文件列表
def get_history_files():
    if os.path.exists(HISTORY_DIR):
        return [f for f in os.listdir(HISTORY_DIR) if f.endswith('.json')]
    return []

# 加载指定的历史记录文件
def load_history_file(file_name):
    file_path = os.path.join(HISTORY_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None

@app.route('/')
def index():
    history_files = get_history_files()
    return render_template_string(HTML, history_files=history_files)

@app.route('/load_history', methods=['GET'])
def load_history():
    file_name = request.args.get('file')
    if not file_name:
        return jsonify({'error': 'Missing file parameter'}), 400
    data = load_history_file(file_name)
    if data is None:
        return jsonify({'error': 'File not found'}), 404
    return jsonify(data)

# HTML模板代码
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Chat History</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            height: 100vh;
            margin: 0;
        }
        .sidebar {
            width: 200px;
            background-color: #f4f4f9;
            padding: 20px;
            border-right: 1px solid #ccc;
        }
        .sidebar h2 {
            text-align: center;
            color: #333;
        }
        .sidebar ul {
            list-style: none;
            padding: 0;
        }
        .sidebar li {
            padding: 10px;
            border-bottom: 1px dashed #ccc;
            cursor: pointer;
        }
        .chat-container {
            flex: 1;
            padding: 20px;
            background-color: #fff;
        }
        .chat-container h1 {
            text-align: center;
            color: #333;
        }
        .response {
            margin-top: 20px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>历史记录</h2>
        <ul id="historyList">
            {% for file in history_files %}
            <li onclick="loadHistory('{{ file }}')">{{ file }}</li>
            {% endfor %}
        </ul>
    </div>
    <div class="chat-container">
        <h1>聊天内容</h1>
        <div class="response" id="response"></div>
    </div>
    <script>
        function loadHistory(file) {
            fetch(`/load_history?file=${file}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('response').innerText = data.error;
                    } else {
                        document.getElementById('response').innerText = JSON.stringify(data, null, 2);
                    }
                })
                .catch(error => {
                    document.getElementById('response').innerText = '加载失败';
                });
        }
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)