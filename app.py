from flask import Flask, render_template , request , jsonify , session
import os
import re
import uuid
import json
from groq import Groq
from config import Config
from datetime import datetime
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem' 
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_sessions') 
app.secret_key = '1234'
Session(app)
client = Groq(api_key=Config.GROQ_API_KEY)

if not os.path.exists(app.config['SESSION_FILE_DIR']):
    os.makedirs(app.config['SESSION_FILE_DIR'])

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

@app.route('/fetch_past_patient_details',methods=['POST'])
def fetch_past_patient_details():
    try:
        data = request.json
        id = data['id']
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    
import json

def process_patient_data(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        if "Weight" in data and "Height" in data:
            weight = data["Weight"]
            height = data["Height"]
            height_in_meters = height / 100
            bmi = weight / (height_in_meters ** 2)
            bmi_value = round(bmi, 2)
            data["BMI"] = bmi_value
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            #print(json.dumps(data, indent=4))
        else:
            print("Skipping as either Weight or Height is missing.")

    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print("Error: The file contains invalid JSON.")
    
def extract_patient_details(conversation):
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
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            response_text = match.group(0)
        patient_details = json.loads(response_text)
        file_name = 'patient_personal_details'
        file_path = save_patient_details_to_file(patient_details, file_name , unique_id='PAT574')
    except (json.JSONDecodeError, AttributeError):
        return "error : The model response could not be parsed as valid JSON."

    return file_path

def extract_prescription_details(conversation):
    prompt = (
        f"""
        Extract the following prescription details from the provided doctor-patient conversation accurately and return the results strictly as a valid JSON object with the specified keys:
        - Tablet (a list of tablets with the following details):
          - Name
          - When should be consumed (before or after food)
          - Timing (breakfast, lunch, dinner)
          - Frequency (e.g., twice a day, once a day)
        - Injection (a list of injections with the following details):
          - Name
          - Dosage (e.g., 10 mg)
          - Frequency (e.g., once a day)
        - Revisiting (when should the patient revisit the doctor)

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

    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            response_text = match.group(0)
        
        prescription_details = json.loads(response_text)
        print("Extracted Prescription Details:", prescription_details)

        file_name = 'patient_prescription_details'
        file_path = save_patient_details_to_file(prescription_details, file_name, unique_id='PAT574')
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error: {e}")
        return "error : The model response could not be parsed as valid JSON."

    return file_path

def extract_diet_plan(conversation):
    prompt = (
        f"""
        Extract the following diet plan details from the provided doctor-patient conversation accurately and return the results strictly as a valid JSON object with the specified keys:
        - Breakfast (a list of breakfast items with the following details):
          - Food item (e.g., Oatmeal, eggs, fruit)
          - Portion size (e.g., 1 cup, 2 eggs)
          - Instructions (e.g., eat with milk, include nuts)
          - Frequency (e.g., once a day)
        - Lunch (a list of lunch items with the following details):
          - Food item (e.g., Salad, grilled chicken)
          - Portion size (e.g., 1 bowl, 200 grams)
          - Instructions (e.g., include olive oil dressing, avoid bread)
          - Frequency (e.g., once a day)
        - Dinner (a list of dinner items with the following details):
          - Food item (e.g., Soup, steamed vegetables)
          - Portion size (e.g., 1 bowl, 150 grams)
          - Instructions (e.g., avoid fried food, eat slowly)
          - Frequency (e.g., once a day)

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

    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            response_text = match.group(0)

        diet_plan_details = json.loads(response_text)

        file_name = 'patient_diet_plan_details'
        file_path = save_patient_details_to_file(diet_plan_details, file_name, unique_id='PAT574')
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error: {e}")
        return "error : The model response could not be parsed as valid JSON."

    return file_path

def extract_care_management(conversation):
    prompt = (
        f"""
        Extract the care management and recommendations from the provided doctor-patient conversation. 
        Return the result as a detailed paragraph summarizing the care instructions, lifestyle changes, 
        and any health recommendations the doctor mentioned.

        Ensure the result is a properly formatted JSON object with the following structure:
        {{
          "care_management_recommendations": "<detailed paragraph summarizing the care plan>"
        }}

        If no recommendations are mentioned in the conversation, return the value as None.
        Ensure the JSON is properly formatted with no extra text or comments outside the structure.

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

    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            response_text = match.group(0)

        care_management_details = json.loads(response_text)

        file_name = 'patient_care_management_details'
        file_path = save_patient_details_to_file(care_management_details, file_name, unique_id='PAT574')
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Error: {e}")
        return "error : The model response could not be parsed as valid JSON."

    return file_path
    
@app.route('/set_patient_details',methods=['POST'])
def set_patient_details():
    try:
        session['patient_id'] = 'PAT574'
        return jsonify({"message": "Patient ID set successfully!", "patient_id": session['patient_id']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_report', methods=['POST'])
def generate_request():
    file_path = session.get('transcript_path')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            transcripts = data.get("transcripts", [])
            if not transcripts:
                return jsonify({"error": "No transcripts found in the file"}), 400
            conversation = transcripts[0].get("transcript")
            patient_details_file_path = extract_patient_details(conversation)
            diet_plan_file_path = extract_diet_plan(conversation)
            prescription_file_path = extract_prescription_details(conversation)
            care_management_file_path = extract_care_management(conversation)
            process_patient_data(patient_details_file_path)

    except (json.JSONDecodeError, FileNotFoundError) as e:
        return f"Error reading the file: {e}"

    return jsonify({
        "message": "Report generated successfully.",
        "patient_details_path": str(patient_details_file_path),
        "diet_plan_path": str(diet_plan_file_path),
        "prescription_path": str(prescription_file_path),
        "care_management_path": str(care_management_file_path)
    })

if __name__ == '__main__':
    app.run(debug=True,port=5000)