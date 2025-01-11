from flask import Flask, render_template , request , jsonify
import os
import re
import uuid
import json
from groq import Groq
from config import Config
from datetime import datetime

app = Flask(__name__)
client = Groq(api_key=Config.GROQ_API_KEY)

def save_patient_details_to_file(patient_details, file_name , unique_id):
    date = datetime.now().strftime("%Y-%m-%d")
    folder_path = f"static/patient_details/{unique_id}/{date}"
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{file_name}.json")
    with open(file_path, 'w') as json_file:
        json.dump(patient_details, json_file, indent=4)
    return file_path

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        name = data['name']
        address = data['address']
        hospital_name = data['hospital_name']
        contact_number = data['contact_number']
        sign = data['sign']
        education_qualification = data['education_qualification']
        email = data['email']
        password = data['password']

        unique_id = "DOC" + str(uuid.uuid4().int)[:3]
        
        base_folder = "static/doctor_details"
        doctor_folder = os.path.join(base_folder, unique_id)
        os.makedirs(doctor_folder, exist_ok=True)

        doctor_data = {
            "name": name,
            "address": address,
            "hospital_name": hospital_name,
            "contact_number": contact_number,
            "sign": sign,
            "education_qualification": education_qualification,
            "email": email,
            "password": password, 
            "unique_id": unique_id
        }
        json_path = os.path.join(doctor_folder, "doc_details.json")
        with open(json_path, 'w') as json_file:
            json.dump(doctor_data, json_file, indent=4)
        return jsonify({"message": "Doctor signed up successfully!", "unique_id": unique_id}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        base_folder = "static/doctor_details"
        if not os.path.exists(base_folder):
            return jsonify({"error": "No doctors registered yet!"}), 404

        for folder in os.listdir(base_folder):
            doc_path = os.path.join(base_folder, folder, "doc_details.json")
            if os.path.exists(doc_path):
                with open(doc_path, 'r') as file:
                    doctor_data = json.load(file)
                    if doctor_data['email'] == email and doctor_data['password'] == password:
                        return jsonify({"message": "Login successful!", "unique_id": doctor_data['unique_id']}), 200

        return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/extract_patient_details', methods=['POST'])
def extract_patient_details():
    data = request.json
    conversation = data.get("conversation", "")

    prompt = (
        f"""
        Extract the following patient details from the provided doctor-patient conversation accurately and return the results strictly as a valid JSON object with the specified keys:
        - Name:
        - Age:
        - Gender:
        - Blood group:
        - Weight:
        - Height:
        - Contact number:

        If any of these fields are not mentioned in the conversation, return the value as None without any explanation.
        Ensure the response is a properly formatted JSON object and contains no additional text or comments outside the JSON structure.

        Conversation:
        {conversation}
        """
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    response_text = chat_completion.choices[0].message.content
    print(response_text)

    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            response_text = match.group(0)
        patient_details = json.loads(response_text)
        file_name = 'patient_personal_details'
        file_path = save_patient_details_to_file(patient_details, file_name , unique_id='PAT574')
    except (json.JSONDecodeError, AttributeError):
        return jsonify({"error": "The model response could not be parsed as valid JSON.", "response": response_text}), 500

    return jsonify({"message": "Patient details successfully saved", "file_path": file_path})

if __name__ == '__main__':
    app.run(debug=True)
