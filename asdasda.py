import json
import logging
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
from flask import Flask, request, render_template

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_folders = [
    '1. Course Outline,CO-PO file,Course Report',
    '2. Supporting Materials',
    '3. Section-wise List of Teachers',
    '4. Questions,Answer Sheets,Other,documents',
]
section_folders = [
    '1. C.T. Questions with Representative Answer Sheet',
    '2. Assignment and Presentation',
    '3. Midterm Answer Sheets',
    '4. Final Answer Sheets',
    '5. CO Attainment file,Final tabulation,Attendance sheet',
]
class_test_folders = ['Class Test-1', 'Class Test-2', 'Class Test-3']

executor = ThreadPoolExecutor(max_workers=10)

def create_folder_in_db(name, parent_id=None):
    max_retries = 50
    sleep_time = 2
    timeout = 500
    for attempt in range(max_retries):
        try:
            url = 'https://drive.zohirrayhan.com/api/v1/folders'
            headers = {
                'accept': 'application/json',
                'Authorization': 'Bearer 1|IFV0y9pP927NiTRFAG2b1qquaxLI4LrCEoxhkadV',
                'Content-Type': 'application/json',
            }
            data = {"name": name, "parentId": parent_id}
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=timeout)
            if response.status_code == 200:
                folder_id = response.json()['folder']['id']
                return folder_id
            else:
                logger.error(f"Error creating folder {name}: {response.content}")
                time.sleep(sleep_time)
                sleep_time *= 2
        except Exception as e:
            logger.error(f"Exception occurred while creating folder {name}: {e}")
            time.sleep(sleep_time)
            sleep_time *= 2
    logger.error(f"Failed to create folder {name} after {max_retries} retries")
    return None

def recursive_folder_creation(parent_id, folder_structure):
    futures = []
    for folder in folder_structure:
        future = executor.submit(create_folder_in_db, folder, parent_id)
        futures.append(future)
        if folder == base_folders[-1]:
            for future in futures:
                new_folder_id = future.result()
                if new_folder_id:
                    recursive_folder_creation(new_folder_id, section_folders)
        elif folder == section_folders[0]:
            for future in futures:
                new_folder_id = future.result()
                if new_folder_id:
                    recursive_folder_creation(new_folder_id, class_test_folders)

def process_excel_file(file_path, session_name):
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1', keep_default_na=False)
        root_folder_id = create_folder_in_db(session_name)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return
    
    current_course_name = None
    course_folder_id = None
    docs_folder_id = None
    
    for index, row in df.iterrows():
        course_name = str(row.get('Course Name ', '')).strip()
        section = str(row.get('Section', '')).strip()
        teacher_name = str(row.get('Teacher Name', '')).strip().replace(' ', '_')
        
        if course_name and course_name.lower() != 'course name':
            current_course_name = course_name.replace(' ', '_')
            course_folder_id = create_folder_in_db(current_course_name, root_folder_id)
            for folder in base_folders:
                new_folder_id = create_folder_in_db(folder, course_folder_id)
                if folder == base_folders[-1]:
                    docs_folder_id = new_folder_id
        
        if section and teacher_name and course_folder_id and docs_folder_id:
            formatted_section_name = f"{section}_{teacher_name}"
            section_folder_id = create_folder_in_db(formatted_section_name, docs_folder_id)
            recursive_folder_creation(section_folder_id, section_folders)
    logger.info("Folder structures created successfully!")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session_name = request.form['session_name'].strip().replace(' ', '_')
        file = request.files['file']
        if file:
            _, temp_filename = tempfile.mkstemp()
            file.save(temp_filename)
            process_excel_file(temp_filename, session_name)
            os.remove(temp_filename)
            return 'Folder structures created successfully!'
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
