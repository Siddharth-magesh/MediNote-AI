from flask import Flask, render_template , request , jsonify
import os
import uuid
import json

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
