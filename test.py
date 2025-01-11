import os
from groq import Groq
import json

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

# Example conversation input
conversation = """
Hello, what is your name and age? My name is John Doe, and I am 32 years old. Great, can you tell me your gender and blood group? I am male, and my blood group is O+. What about your weight and height? I weigh 75 kg and my height is 180 cm. Please provide your contact number. Sure, it's 9876543210.
"""

# Prompt for Groq LLM
prompt = (
    f"""
    Extract the following patient details from the provided doctor-patient conversation:
    - Name
    - Age
    - Gender
    - Blood group
    - Weight
    - Height
    - Contact number
    
    If any of these fields are not mentioned, return their values as None. 
    Provide the final output as a structured JSON object with the exact keys mentioned above.
    
    Conversation:
    {conversation}
    """
)

# Call the Groq API for patient details extraction
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="llama-3.3-70b-versatile",
)

# Print the generated JSON response
response_text = chat_completion.choices[0].message.content
print("Extracted Patient Details (JSON):")
print(response_text)

# Attempt to parse the response as JSON
try:
    patient_details = json.loads(response_text)
    print(patient_details)
except json.JSONDecodeError:
    print("Error: The model response could not be parsed as valid JSON.")
