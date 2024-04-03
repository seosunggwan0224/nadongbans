from flask import Flask, render_template, request, jsonify
import pymysql
import pyttsx3
import speech_recognition as sr
import datetime
from openai import OpenAI

app = Flask(__name__)

# MySQL 연결
conn = pymysql.connect(host='localhost', user='LeeGiSeung', password='Hh134679852!', db="Health", charset='utf8')
cursor = conn.cursor()

# 음성 인식 관련 설정
recognizer = sr.Recognizer()
engine = pyttsx3.init()
today = datetime.date.today()
insert_sql = '''INSERT INTO user (Alcohol, Outside, Exercise, today) VALUES (%s, %s, %s, %s)'''
cursor = conn.cursor()
api = "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"
client = OpenAI(api_key=api)


@app.route('/')
def index():
    # 데이터베이스에서 정보를 가져옴
    cursor.execute("SELECT * FROM user")
    data = cursor.fetchall()
    return render_template('index.html', data=data)

@app.route('/process_voice_data', methods=['POST'])
def process_voice_data():
    try:
        with sr.Microphone() as source:
            print("오늘 하루 어땠는지 말씀해주세요.")
            audio = recognizer.listen(source)
            # Google Web Speech API를 이용해 음성을 텍스트로 변환
            text = recognizer.recognize_google(audio, language="ko-KR")
            print("음성 인식 결과:", text)

# Drink Alcohol
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "음주를 했으면 1을 반환하고 음주를 하지 않았으면 2를 반환해줘"},
                {"role": "user", "content": text}
            ]
        )

        if "1" in completion.choices[0].message.content:
            Alcohol = 1
        else:
            Alcohol = 0

        print("음주 여부 : ", Alcohol)

        # Outside
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "외출을 했으면 1을 반환하고 외출을 하지 않았으면 2를 반환해줘"},
                {"role": "user", "content": text}
            ]
        )
        if "1" in completion.choices[0].message.content:
            OutSide = 1
        else:
            OutSide = 0

        print("외출 여부 : ", OutSide)

        # Exercise
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "운동을 했으면 1을 반환하고 운동을 하지 않았으면 2를 반환해줘"},
                {"role": "user", "content": text}
            ]
        )
        if "1" in completion.choices[0].message.content:
            Exercise = 1
        else:
            Exercise = 0

        print("운동 여부 : ", Exercise)

        cursor.execute(insert_sql, (Alcohol, OutSide, Exercise, today))

        #Alcohol : 음주 여부
        #OutSide : 외출 여부
        #Exercise : 운동 여부
        #today : 날짜
        conn.commit()

        # 처리 완료 후 데이터베이스에서 정보를 가져와서 반환
        cursor.execute("SELECT * FROM user")
        data = cursor.fetchall()
        return jsonify(data)

    except sr.UnknownValueError:
        print("음성을 인식할 수 없습니다.")
        return jsonify({'error': '음성을 인식할 수 없습니다.'})
    except sr.RequestError as e:
        print(f"음성 인식 서비스에 접근할 수 없습니다: {e}")
        return jsonify({'error': '음성 인식 서비스에 접근할 수 없습니다.'})

if __name__ == '__main__':
    app.run(debug=True)
