from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML = '''
<form action="/" method="post">
  <input type="text" name="prompt" placeholder="输入问题...">
  <button>发送</button>
</form>
<pre>{{ response }}</pre>
'''

@app.route('/', methods=['GET', 'POST'])
def chat():
    response = ""
    if request.method == 'POST':
        prompt = request.form['prompt']
        resp = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': 'deepseek-r1:1.5b', 'prompt': prompt, 'stream': False}
        )
        response = resp.json()['response']
    return render_template_string(HTML, response=response)

if __name__ == '__main__':
    app.run(port=5000)