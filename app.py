from flask import Flask, render_template, request, redirect, url_for
import openai
from config import api_key
import json


app = Flask(__name__)


openai.api_key=api_key
def get_completion(prompt, model="gpt-3.5-turbo"):

    messages = [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(

    model=model,

    messages=messages,

    temperature=0,

)

    return response.choices[0].message["content"]
# Sample fields and levels
fields = ['Artificial Intelligence', 'Chemistry', 'Machine Learning', 'Python', 'Mathematics', 'Biology', 'Physics', 'Web Development', 'History', 'Geography']
levels = [1, 2, 3]

# Define the questions, options, and answers lists outside the JSON format
questions = ["Question1", "Question 2", "Question 3", ...,"Question 10"]
options = [["Option A", "Option B", "Option C", "Option D"], ["Option A", "Option B", "Option C", "Option D"], ...]
answers = ["A", "B", "C", ...]

# Create the JSON format with questions, options, and answers
dic_format ={
        "Questions": questions,
        "Options": options,
        "Answer": answers
    }


@app.route('/')
def index():
    return render_template('index.html', fields=fields, levels=levels)

@app.route('/generate', methods=['POST'])
def generate_mcqs():
    field = request.form['field']
    level = int(request.form['level'])
    # Now, use the JSON format in your prompt
    prompt = f"""
    Act as an expert in {field}. Considering the three levels in this specific field:
    Level 1: MCQs should be easy as an entry level.
    Level 2: MCQs should be tricky.
    Level 3: MCQs should be tricky and tough as it is the highest level.

    Generate 10 MCQs considering level {level} in a appropriate JSON format with options. Make sure that  property names (keys) to be enclosed in double quotes (") Here is an example of the JSON format::
    {dic_format}
    """
    global mcq_data
    try:
        data=get_completion(prompt)
    except:
        return 'Connection cannot be established'
    
    mcq_data=json.loads(data)

    # Add question indices to the MCQ data for rendering
    mcq_data['QuestionIndices'] = list(range(len(mcq_data['Questions'])))

    return render_template('mcqs.html', mcq_data=mcq_data)
    

@app.route('/evaluate', methods=['POST'])
def evaluate_answers():
    user_answers = {}
    mcq_data = request.form.to_dict()

    # Extract user answers from the form data
    for key, value in mcq_data.items():
        if key.startswith('question'):
            question_number = key.split('_')[0].replace('question', '')
            user_answers[question_number] = value

    # Evaluate user answers
    score = evaluate_user_answers(user_answers)

    # Display the score page
    return render_template('score.html', score=score)

def evaluate_user_answers(user_answers):
    correct_answers = {str(i + 1): answer for i, answer in enumerate(mcq_data["Answer"])}
    score = sum(user_answers.get(q, '') == correct_answers[q] for q in correct_answers)
    return score

if __name__ == '__main__':
    app.run(debug=True)
