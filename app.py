from flask import Flask, render_template, request
import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():

    topic = request.form['topic']

    prompt = f"""
    Generate 5 MCQ questions on {topic}.
    Return ONLY valid JSON.
    Each answer MUST be exactly one of the option strings.
    Example:
    [
    {{
        "question":"What is the capital of France?",
        "options":["Paris","London","Berlin","Rome"],
        "answer":"Paris"
    }}
    ]
    """

    response = model.generate_content(prompt)

    text = response.text

    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    questions = json.loads(text)

    return render_template(
        "quiz.html",
        questions=questions,
        topic=topic
    )

@app.route('/score', methods=['POST'])
def score():

    total = int(request.form['total'])
    score = 0

    for i in range(total):

        selected = request.form.get(f"q{i}")

        answer = request.form.get(f"a{i}")
        # print(f"Question {i}")
        # print("Selected:", repr(selected))
        # print("Answer:", repr(answer))

        if selected == answer:
            score += 1

    percentage = round((score/total)*100,2)

    return f"""
    <h1>Quiz Result</h1>
    <h2>Score: {score}/{total}</h2>
    <h2>Percentage: {percentage}%</h2>
    <a href='/'>Try Another Quiz</a>
    """

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True)