from flask import Flask, render_template , request , jsonify , send_file
import os
import re
import uuid
import json
from groq import Groq
from config import Config
from datetime import datetime
import cv2
import textwrap
from PIL import Image

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
    return render_template('Analyse.html')

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

BASE_PATH = r"D:/MediNote-AI/static/"

def generate_images(patient_details_file_path,care_management_file_path, diet_plan_file_path,prescription_file_path):

    template_path = os.path.join(BASE_PATH, "1.png")
    image = cv2.imread(template_path)

    template_path2 = os.path.join(BASE_PATH, "2.png")
    image2 = cv2.imread(template_path2)

    doctor_file_path = os.path.join(BASE_PATH, "doctor_details/DOC856/doc_details.json")
    with open(patient_details_file_path, "r") as patient_file:
        patient_data = json.load(patient_file)

    with open(doctor_file_path, "r") as doctor_file:
        doctor_data = json.load(doctor_file)

    with open(prescription_file_path, "r") as prescription_file:
        prescription_data = json.load(prescription_file)

    with open(care_management_file_path, "r") as care_file:
        care_data = json.load(care_file)

    with open(diet_plan_file_path, "r") as diet_file:
        diet_data = json.load(diet_file)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    color = (0, 0, 0)
    thickness = 2

    positions = {
        "patient": {
            "Name": (304, 437),
            "Age": (300, 497),
            "Gender": (304, 559),
            "Contact number": (310, 611),
            "Weight": (306, 675),
            "Height": (308, 735),
            "Blood group": (308, 790),
            "BMI": (308, 854),
        },
        "doctor": {
            "name": (964, 437),
            "address": (964, 498),
            "contact_number": (974, 557),
        },
    }

    table_positions = [
        {"Name": (52, 1285), "Timing": (404, 1285), "When": (738, 1285), "Frequency": (1055, 1285)},
        {"Name": (52, 1402), "Timing": (404, 1402), "When": (738, 1402), "Frequency": (1055, 1402)},
        {"Name": (52, 1522), "Timing": (404, 1522), "When": (738, 1522), "Frequency": (1055, 1522)},
        {"Name": (52, 1633), "Timing": (404, 1633), "When": (738, 1633), "Frequency": (1055, 1633)},
    ]

    meal_positions = {
        "Breakfast": (225, 530),
        "Lunch": (225, 765),
        "Dinner": (225, 955)
    }

    meal_box_width = 900
    care_box_width = image2.shape[1] - 2 * 40 - 100
    care_position = (40, 1302)

    def draw_text_box(image, position, lines, box_width, line_spacing=30, margin=10):
        x, y = position
        box_height = len(lines) * line_spacing + 2 * margin
        cv2.rectangle(image, (x, y), (x + box_width, y + box_height), (255, 255, 255), -1)
        cv2.rectangle(image, (x, y), (x + box_width, y + box_height), (255, 255, 255), 2)

        for i, line in enumerate(lines):
            text_position = (x + margin, y + margin + i * line_spacing)
            cv2.putText(image, line, text_position, font, font_scale, color, thickness, cv2.LINE_AA)

    care_recommendations = care_data.get("care_management_recommendations", "N/A")
    wrapped_care_recommendations = textwrap.wrap(care_recommendations, width=95)
    draw_text_box(image2, care_position, wrapped_care_recommendations, care_box_width)

    for meal, position in meal_positions.items():
        meal_data = diet_data.get(meal, [{}])[0]
        lines = [
            f"{meal_data.get('Food item', 'N/A')}",
            f"{meal_data.get('Portion size', 'N/A')}",
            f"{meal_data.get('Instructions', 'N/A')}",
            f"{meal_data.get('Frequency', 'N/A')}"
        ]
        draw_text_box(image2, position, lines, meal_box_width)

    output_path2 = os.path.join(BASE_PATH, "updated_diet_plan.png")
    cv2.imwrite(output_path2, image2)

    for key, position in positions["patient"].items():
        text = f"{patient_data[key]}"
        cv2.putText(image, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

    for key, position in positions["doctor"].items():
        text = f"{doctor_data[key]}"
        cv2.putText(image, text, position, font, font_scale, color, thickness, cv2.LINE_AA)

    for i, tablet in enumerate(prescription_data["Tablet"][:4]):
        for key, position in table_positions[i].items():
            text = tablet.get(key, "N/A")
            cv2.putText(image, text, position, font, 0.8, color, 1, cv2.LINE_AA)

    revisit_position = (243, 1845)
    revisit_text = f"{prescription_data.get('Revisiting', 'N/A')}"
    cv2.putText(image, revisit_text, revisit_position, font, font_scale, color, thickness, cv2.LINE_AA)

    output_path = os.path.join(BASE_PATH, "updated_prescription.png")
    cv2.imwrite(output_path, image)

    return output_path, output_path2

@app.route('/generate_report', methods=['POST'])
def generate_images_endpoint():
    patient_id = "PAT574"
    file_path = r'D:\MediNote-AI\static\patient_details\PAT574\2025-01-12\transcript.json'
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            transcripts = data.get("transcripts", [])
            if not transcripts:
                return jsonify({"error": "No transcripts found in the file"}), 400
            conversation = transcripts[0].get("transcript")
            patient_details_file_path = extract_patient_details(conversation)
            print("done")
            diet_plan_file_path = extract_diet_plan(conversation)
            print("done")
            prescription_file_path = extract_prescription_details(conversation)
            print("done")
            care_management_file_path = extract_care_management(conversation)
            print("done")
            process_patient_data(patient_details_file_path)
            img1_path , img2_path = generate_images(patient_details_file_path,care_management_file_path,diet_plan_file_path,prescription_file_path)

    except (json.JSONDecodeError, FileNotFoundError) as e:
        return f"Error reading the file: {e}"

    return render_template('prescription page 1.html')

@app.route('/render_next_page')
def render_next_page():
    return render_template('prescription page 2.html')

@app.route('/render_previous_page')
def render_previous_page():
    return render_template('prescription page 1.html')

@app.route('/print_prescription')
def print_prescription():
    try:
        image1_path = r'D:\MediNote-AI\static\updated_prescription.png'
        image2_path = r'D:\MediNote-AI\static\updated_diet_plan.png'
        
        pdf_dir = r'D:\MediNote-AI\static'
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)

        pdf_path = os.path.join(pdf_dir, 'combined_prescription.pdf')
        if not os.path.exists(image1_path) or not os.path.exists(image2_path):
            return jsonify({"error": "One or more images not found"}), 404
        image1 = Image.open(image1_path)
        image2 = Image.open(image2_path)
        image1.save(pdf_path, "PDF", resolution=100.0)
        image2.save(pdf_path, "PDF", resolution=100.0, append=True)
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True,port=5000)