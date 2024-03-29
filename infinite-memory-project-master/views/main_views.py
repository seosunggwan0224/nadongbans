from flask import Blueprint, Flask, render_template, request
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from .. import chat_main


views_bp = Blueprint('main', __name__, url_prefix='/')

@views_bp.route('/chat', methods=('GET', 'POST'))
def chat_page():
    if request.method == 'GET':
        return render_template('index2.html')
    elif request.method == 'POST':
        data = request.get_json()
        transcript = data['text']
        print(transcript)  # 음성인식 잘됨 확인
        a_of_chat_main = chat_main(transcript)
        print(a_of_chat_main)
        return render_template('index2.html', text=transcript, output=a_of_chat_main)
