"""Integration tests for patient API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPatientCreate:
    """Tests for patient creation endpoint."""

    async def test_create_patient_success(self, authenticated_client: AsyncClient):
        """Test successful patient creation."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "phone_primary": "+919876543210",
                "date_of_birth": "1990-05-15",
                "gender": "male",
                "blood_group": "A+",
                "email": "john.doe@example.com",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["phone_primary"] == "+919876543210"
        assert data["patient_id"].startswith("PAT-")
        assert data["status"] == "active"
        assert "id" in data

    async def test_create_patient_minimal(self, authenticated_client: AsyncClient):
        """Test patient creation with minimal data."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Jane",
                "last_name": "Smith",
                "phone_primary": "+919876543211",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"

    async def test_create_patient_with_address(self, authenticated_client: AsyncClient):
        """Test patient creation with address."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Test",
                "last_name": "Address",
                "phone_primary": "+919876543212",
                "address": {
                    "line1": "123 Main St",
                    "line2": "Apt 4B",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India",
                },
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["address"]["city"] == "Mumbai"
        assert data["address"]["state"] == "Maharashtra"

    async def test_create_patient_with_emergency_contact(
        self, authenticated_client: AsyncClient
    ):
        """Test patient creation with emergency contact."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Test",
                "last_name": "Emergency",
                "phone_primary": "+919876543213",
                "emergency_contact": {
                    "name": "Emergency Person",
                    "relation": "Spouse",
                    "phone": "+919876543299",
                },
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["emergency_contact"]["name"] == "Emergency Person"

    async def test_create_patient_with_medical_info(
        self, authenticated_client: AsyncClient
    ):
        """Test patient creation with medical information."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Test",
                "last_name": "Medical",
                "phone_primary": "+919876543214",
                "allergies": ["Penicillin", "Peanuts"],
                "chronic_conditions": ["Diabetes", "Hypertension"],
                "current_medications": ["Metformin", "Amlodipine"],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "Penicillin" in data["allergies"]
        assert "Diabetes" in data["chronic_conditions"]

    async def test_create_patient_duplicate_phone(
        self, authenticated_client: AsyncClient
    ):
        """Test patient creation with duplicate phone number."""
        # Create first patient
        await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "First",
                "last_name": "Patient",
                "phone_primary": "+919876543215",
            },
        )

        # Try to create second patient with same phone
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Second",
                "last_name": "Patient",
                "phone_primary": "+919876543215",
            },
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    async def test_create_patient_invalid_phone(
        self, authenticated_client: AsyncClient
    ):
        """Test patient creation with invalid phone number."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Test",
                "last_name": "Invalid",
                "phone_primary": "invalid-phone",
            },
        )

        assert response.status_code == 422

    async def test_create_patient_invalid_gender(
        self, authenticated_client: AsyncClient
    ):
        """Test patient creation with invalid gender."""
        response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Test",
                "last_name": "Invalid",
                "phone_primary": "+919876543216",
                "gender": "invalid",
            },
        )

        assert response.status_code == 422

    async def test_create_patient_unauthorized(self, client: AsyncClient):
        """Test patient creation without authentication."""
        response = await client.post(
            "/api/v1/patients",
            json={
                "first_name": "Test",
                "last_name": "Unauthorized",
                "phone_primary": "+919876543217",
            },
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestPatientList:
    """Tests for patient list endpoint."""

    async def test_list_patients_empty(self, authenticated_client: AsyncClient):
        """Test listing patients when empty."""
        response = await authenticated_client.get("/api/v1/patients")

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert data["skip"] == 0
        assert data["limit"] == 20

    async def test_list_patients_with_data(self, authenticated_client: AsyncClient):
        """Test listing patients with data."""
        # Create some patients
        for i in range(3):
            await authenticated_client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"Patient{i}",
                    "last_name": "Test",
                    "phone_primary": f"+9198765432{20 + i}",
                },
            )

        response = await authenticated_client.get("/api/v1/patients")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3

    async def test_list_patients_pagination(self, authenticated_client: AsyncClient):
        """Test patient list pagination."""
        # Create 5 patients
        for i in range(5):
            await authenticated_client.post(
                "/api/v1/patients",
                json={
                    "first_name": f"Page{i}",
                    "last_name": "Test",
                    "phone_primary": f"+9198765432{30 + i}",
                },
            )

        # Get first page
        response = await authenticated_client.get("/api/v1/patients?limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

        # Get second page
        response = await authenticated_client.get("/api/v1/patients?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    async def test_list_patients_filter_status(self, authenticated_client: AsyncClient):
        """Test patient list filtering by status."""
        response = await authenticated_client.get("/api/v1/patients?status=active")

        assert response.status_code == 200
        data = response.json()
        for patient in data["results"]:
            assert patient["status"] == "active"

    async def test_list_patients_unauthorized(self, client: AsyncClient):
        """Test patient list without authentication."""
        response = await client.get("/api/v1/patients")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestPatientSearch:
    """Tests for patient search endpoint."""

    async def test_search_by_name(self, authenticated_client: AsyncClient):
        """Test searching patients by name."""
        # Create a patient
        await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Searchable",
                "last_name": "Person",
                "phone_primary": "+919876543240",
            },
        )

        response = await authenticated_client.get(
            "/api/v1/patients/search?q=Searchable"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        found = any(p["first_name"] == "Searchable" for p in data["results"])
        assert found

    async def test_search_by_phone(self, authenticated_client: AsyncClient):
        """Test searching patients by phone number."""
        # Create a patient
        await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Phone",
                "last_name": "Search",
                "phone_primary": "+919876543241",
            },
        )

        response = await authenticated_client.get(
            "/api/v1/patients/search?q=9876543241"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_search_by_patient_id(self, authenticated_client: AsyncClient):
        """Test searching patients by patient ID."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "ID",
                "last_name": "Search",
                "phone_primary": "+919876543242",
            },
        )
        patient_id = create_response.json()["patient_id"]

        response = await authenticated_client.get(
            f"/api/v1/patients/search?q={patient_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    async def test_search_no_results(self, authenticated_client: AsyncClient):
        """Test search with no results."""
        response = await authenticated_client.get(
            "/api/v1/patients/search?q=nonexistent12345"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0


@pytest.mark.asyncio
class TestPatientGet:
    """Tests for get patient endpoint."""

    async def test_get_patient_by_uuid(self, authenticated_client: AsyncClient):
        """Test getting patient by UUID."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Get",
                "last_name": "ByUUID",
                "phone_primary": "+919876543250",
            },
        )
        patient_id = create_response.json()["id"]

        response = await authenticated_client.get(f"/api/v1/patients/{patient_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == patient_id
        assert data["first_name"] == "Get"

    async def test_get_patient_by_patient_id(self, authenticated_client: AsyncClient):
        """Test getting patient by patient ID."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Get",
                "last_name": "ByPatientID",
                "phone_primary": "+919876543251",
            },
        )
        patient_id = create_response.json()["patient_id"]

        response = await authenticated_client.get(f"/api/v1/patients/{patient_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == patient_id

    async def test_get_patient_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent patient."""
        response = await authenticated_client.get(
            "/api/v1/patients/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestPatientUpdate:
    """Tests for patient update endpoint."""

    async def test_update_patient_name(self, authenticated_client: AsyncClient):
        """Test updating patient name."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Original",
                "last_name": "Name",
                "phone_primary": "+919876543260",
            },
        )
        patient_id = create_response.json()["id"]

        # Update patient
        response = await authenticated_client.patch(
            f"/api/v1/patients/{patient_id}",
            json={
                "first_name": "Updated",
                "last_name": "NewName",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "NewName"

    async def test_update_patient_partial(self, authenticated_client: AsyncClient):
        """Test partial patient update."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Partial",
                "last_name": "Update",
                "phone_primary": "+919876543261",
                "gender": "male",
            },
        )
        patient_id = create_response.json()["id"]

        # Update only one field
        response = await authenticated_client.patch(
            f"/api/v1/patients/{patient_id}",
            json={
                "gender": "female",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["gender"] == "female"
        assert data["first_name"] == "Partial"  # Unchanged

    async def test_update_patient_address(self, authenticated_client: AsyncClient):
        """Test updating patient address."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Address",
                "last_name": "Update",
                "phone_primary": "+919876543262",
            },
        )
        patient_id = create_response.json()["id"]

        # Update address
        response = await authenticated_client.patch(
            f"/api/v1/patients/{patient_id}",
            json={
                "address": {
                    "line1": "456 New St",
                    "city": "Delhi",
                    "state": "Delhi",
                    "country": "India",
                },
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["address"]["city"] == "Delhi"

    async def test_update_patient_status(self, authenticated_client: AsyncClient):
        """Test updating patient status."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Status",
                "last_name": "Update",
                "phone_primary": "+919876543263",
            },
        )
        patient_id = create_response.json()["id"]

        # Update status
        response = await authenticated_client.patch(
            f"/api/v1/patients/{patient_id}",
            json={
                "status": "inactive",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"

    async def test_update_patient_not_found(self, authenticated_client: AsyncClient):
        """Test updating non-existent patient."""
        response = await authenticated_client.patch(
            "/api/v1/patients/00000000-0000-0000-0000-000000000000",
            json={"first_name": "Test"},
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestPatientDelete:
    """Tests for patient delete endpoint."""

    async def test_delete_patient(self, authenticated_client: AsyncClient):
        """Test deleting patient (soft delete)."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Delete",
                "last_name": "Me",
                "phone_primary": "+919876543270",
            },
        )
        patient_id = create_response.json()["id"]

        # Delete patient
        response = await authenticated_client.delete(f"/api/v1/patients/{patient_id}")

        assert response.status_code == 204

        # Verify patient is archived
        get_response = await authenticated_client.get(f"/api/v1/patients/{patient_id}")
        assert get_response.json()["status"] == "archived"

    async def test_delete_patient_not_found(self, authenticated_client: AsyncClient):
        """Test deleting non-existent patient."""
        response = await authenticated_client.delete(
            "/api/v1/patients/00000000-0000-0000-0000-000000000000"
        )

        assert response.status_code == 404


@pytest.mark.asyncio
class TestCheckPhoneDuplicate:
    """Tests for phone duplicate check endpoint."""

    async def test_check_phone_not_duplicate(self, authenticated_client: AsyncClient):
        """Test checking phone that's not a duplicate."""
        response = await authenticated_client.get(
            "/api/v1/patients/check-phone?phone=+919876543280"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_duplicate"] is False

    async def test_check_phone_is_duplicate(self, authenticated_client: AsyncClient):
        """Test checking phone that's a duplicate."""
        # Create a patient
        await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Duplicate",
                "last_name": "Check",
                "phone_primary": "+919876543281",
            },
        )

        response = await authenticated_client.get(
            "/api/v1/patients/check-phone?phone=+919876543281"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_duplicate"] is True

    async def test_check_phone_exclude_self(self, authenticated_client: AsyncClient):
        """Test checking phone excluding own ID."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "Exclude",
                "last_name": "Self",
                "phone_primary": "+919876543282",
            },
        )
        patient_id = create_response.json()["id"]

        response = await authenticated_client.get(
            f"/api/v1/patients/check-phone?phone=+919876543282&exclude_id={patient_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_duplicate"] is False


@pytest.mark.asyncio
class TestPatientHistory:
    """Tests for patient history endpoint."""

    async def test_get_patient_history_empty(self, authenticated_client: AsyncClient):
        """Test getting patient history with no visits."""
        # Create a patient
        create_response = await authenticated_client.post(
            "/api/v1/patients",
            json={
                "first_name": "History",
                "last_name": "Empty",
                "phone_primary": "+919876543290",
            },
        )
        patient_id = create_response.json()["id"]

        response = await authenticated_client.get(
            f"/api/v1/patients/{patient_id}/history"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["results"]) == 0

    async def test_get_patient_history_not_found(
        self, authenticated_client: AsyncClient
    ):
        """Test getting history for non-existent patient."""
        response = await authenticated_client.get(
            "/api/v1/patients/00000000-0000-0000-0000-000000000000/history"
        )

        assert response.status_code == 404
