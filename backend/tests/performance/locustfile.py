"""Load testing with Locust for MediNote-AI API."""

from locust import HttpUser, task, between
import json
import random
import string


def random_string(length: int = 10) -> str:
    """Generate a random string."""
    return "".join(random.choices(string.ascii_letters, k=length))


def random_phone() -> str:
    """Generate a random phone number."""
    return f"+91{random.randint(1000000000, 9999999999)}"


class MediNoteUser(HttpUser):
    """Simulated user for load testing."""

    wait_time = between(1, 3)
    access_token = None
    patient_ids = []

    def on_start(self):
        """Login when user starts."""
        # Register a new user
        email = f"loadtest_{random_string(8)}@example.com"
        password = "TestPass123!"

        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "name": f"Load Test User {random_string(5)}",
            },
        )

        # Login
        response = self.client.post(
            "/api/v1/auth/login",
            data={
                "username": email,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            self.access_token = response.json().get("access_token")

    @property
    def auth_headers(self):
        """Get authorization headers."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    @task(10)
    def list_patients(self):
        """Test listing patients."""
        self.client.get(
            "/api/v1/patients",
            headers=self.auth_headers,
            name="/api/v1/patients [GET]",
        )

    @task(5)
    def search_patients(self):
        """Test searching patients."""
        query = random.choice(["john", "test", "patient", random_string(3)])
        self.client.get(
            f"/api/v1/patients/search?q={query}",
            headers=self.auth_headers,
            name="/api/v1/patients/search [GET]",
        )

    @task(3)
    def create_patient(self):
        """Test creating a patient."""
        response = self.client.post(
            "/api/v1/patients",
            json={
                "first_name": f"Test{random_string(5)}",
                "last_name": f"User{random_string(5)}",
                "phone_primary": random_phone(),
                "gender": random.choice(["male", "female"]),
                "date_of_birth": "1990-01-15",
            },
            headers=self.auth_headers,
            name="/api/v1/patients [POST]",
        )

        if response.status_code == 201:
            patient_id = response.json().get("id")
            if patient_id:
                self.patient_ids.append(patient_id)

    @task(2)
    def get_patient(self):
        """Test getting a specific patient."""
        if self.patient_ids:
            patient_id = random.choice(self.patient_ids)
            self.client.get(
                f"/api/v1/patients/{patient_id}",
                headers=self.auth_headers,
                name="/api/v1/patients/{id} [GET]",
            )

    @task(1)
    def update_patient(self):
        """Test updating a patient."""
        if self.patient_ids:
            patient_id = random.choice(self.patient_ids)
            self.client.patch(
                f"/api/v1/patients/{patient_id}",
                json={
                    "first_name": f"Updated{random_string(5)}",
                },
                headers=self.auth_headers,
                name="/api/v1/patients/{id} [PATCH]",
            )

    @task(2)
    def check_phone_duplicate(self):
        """Test phone duplicate check."""
        phone = random_phone()
        self.client.get(
            f"/api/v1/patients/check-phone?phone={phone}",
            headers=self.auth_headers,
            name="/api/v1/patients/check-phone [GET]",
        )

    @task(1)
    def get_patient_history(self):
        """Test getting patient history."""
        if self.patient_ids:
            patient_id = random.choice(self.patient_ids)
            self.client.get(
                f"/api/v1/patients/{patient_id}/history",
                headers=self.auth_headers,
                name="/api/v1/patients/{id}/history [GET]",
            )

    @task(5)
    def get_current_user(self):
        """Test getting current user info."""
        self.client.get(
            "/api/v1/auth/me",
            headers=self.auth_headers,
            name="/api/v1/auth/me [GET]",
        )

    @task(1)
    def refresh_token(self):
        """Test token refresh."""
        # This would need a refresh token stored
        pass


class ExtractionUser(HttpUser):
    """User specifically for testing extraction endpoints."""

    wait_time = between(2, 5)
    access_token = None

    def on_start(self):
        """Login when user starts."""
        email = f"extract_{random_string(8)}@example.com"
        password = "TestPass123!"

        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": password,
                "name": f"Extraction Test User {random_string(5)}",
            },
        )

        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code == 200:
            self.access_token = response.json().get("access_token")

    @property
    def auth_headers(self):
        """Get authorization headers."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}

    @task(1)
    def extract_patient_details(self):
        """Test patient details extraction."""
        transcript = """
        Doctor: Good morning, what brings you here today?
        Patient: I'm having a severe headache for the past 3 days.
        Doctor: I see. Can you tell me your name and age?
        Patient: My name is Rahul Kumar, I'm 35 years old.
        """

        self.client.post(
            "/api/v1/extraction/patient-details",
            json={"transcript": transcript},
            headers=self.auth_headers,
            name="/api/v1/extraction/patient-details [POST]",
        )

    @task(1)
    def extract_all(self):
        """Test full extraction."""
        transcript = """
        Doctor: What's the problem?
        Patient: I have fever and body pain since yesterday.
        Doctor: Let me check your temperature. It's 101F. I'm prescribing
        Paracetamol 500mg twice daily for 3 days. Also take rest and
        drink plenty of fluids. Come back if fever doesn't subside.
        """

        self.client.post(
            "/api/v1/extraction/all",
            json={
                "transcript": transcript,
                "extract_patient_details": True,
                "extract_symptoms": True,
                "extract_prescription": True,
                "extract_diet_plan": False,
                "extract_care_instructions": True,
            },
            headers=self.auth_headers,
            name="/api/v1/extraction/all [POST]",
        )


# To run:
# pip install locust
# locust -f locustfile.py --host=http://localhost:8000
