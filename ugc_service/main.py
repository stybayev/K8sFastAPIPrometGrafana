from flask import Flask
from core.config import settings
app = Flask(__name__)


@app.route('/hello-world')
def hello_world():
    print('Hello, World!')
    print(settings.project_name)
    return 'Hello, World!'
