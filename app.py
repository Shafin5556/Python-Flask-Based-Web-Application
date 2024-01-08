from flask import Flask, request, render_template, send_from_directory, jsonify, send_file
from flask import Flask, request, render_template, send_from_directory, jsonify, send_file, session, redirect

import openai
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

# Set the secret key
app.secret_key = 'your_random_secret_key_here'



UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/get_pdfs', methods=['GET'])
def get_pdfs():
    files = [f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(
        os.path.join(UPLOAD_FOLDER, f))]
    return jsonify(files)


@app.route('/get_pdf/<filename>', methods=['GET'])
def get_pdf(filename):
    # Update the path to match the location of your PDFs
    path = f'static/uploads/{filename}'
    return send_file(path, as_attachment=True, mimetype='application/pdf')

@app.route('/', methods=['GET'])
def root():
    # You can add any logic here if needed
    return render_template('main.html')  # Updated to 'main.html'

# In your Flask app.py file

@app.route('/join', methods=['POST'])
def join_teacher():
    selected_teacher = request.form.get('selected_teacher')
    
    # Add your logic to join the selected teacher
    # ...

    # Redirect to the dynamic URL based on the selected teacher's name
    return redirect(f'/{selected_teacher}.html')





@app.route('/<teacher>.html', methods=['GET'])
def index(teacher):
    # Retrieve the selected teacher from the session
    selected_teacher = session.get('selected_teacher')
    filename = None
    if request.method == 'POST':
        pdf_file = request.files['file']
        if pdf_file and pdf_file.filename != '':
            filename = secure_filename(pdf_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            pdf_file.save(filepath)
    return render_template('index.html', filename=filename, selected_teacher=teacher)





# @app.route('/static/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


openai.api_key = "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"

# Keep track of previous teaching points
previous_teaching_points = []


def extract_main_teaching_point(text):
    return text.split('.')[0]


def get_openai_response(extracted_text, is_first_page=False):
    model_engine = "gpt-3.5-turbo"

    if is_first_page:
        prompt = f"Provide a  welcome to Daffodil International University students and introduce them to the topic '{extracted_text}'. Then continue to explain the key points of the topic.Note: You don't have to say your name , You can say I am your AI Teacher"
    else:
        prompt = f"Provide a clear and concise educational explanation about '{extracted_text}', continuing from the following previous teaching points: {', '.join(previous_teaching_points)}. The explanation should be geared towards University students, focusing on key points and avoiding jargon."

    messages = [
        {"role": "system", "content": "You are Dr. Sheak Rashed Haider Noori, Associate Professor & Associate Head. You are specialized in generating educational explanations."},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=messages,
        max_tokens=100)

    # Only add the main teaching point if not the first page
    if not is_first_page:
        main_point = extract_main_teaching_point(
            response.choices[0].message['content'])
        previous_teaching_points.append(main_point)

    return response.choices[0].message['content'].strip()


@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    extracted_text = data.get('text')
    page_number = data.get('page')
    print("Page Number")
    print(page_number)
    # Change this based on how you pass the page number
    is_first_page = (page_number == "1")
    speech = get_openai_response(extracted_text, is_first_page)

    return jsonify({'speech': speech})


if __name__ == '__main__':
    app.run(debug=True)
