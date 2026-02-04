"""Initial migration - create all tables

Revision ID: 20260204_000001
Revises:
Create Date: 2026-02-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260204_000001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("hospital_name", sa.String(255), nullable=True),
        sa.Column("hospital_address", sa.Text(), nullable=True),
        sa.Column("qualification", sa.String(255), nullable=True),
        sa.Column("registration_number", sa.String(100), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("signature_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("is_verified", sa.Boolean(), default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_users_email", "users", ["email"])

    # Patients table
    op.create_table(
        "patients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patient_id", sa.String(20), nullable=False, unique=True),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("last_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("blood_group", sa.String(10), nullable=True),
        sa.Column("phone_primary", sa.String(20), nullable=False, unique=True),
        sa.Column("phone_secondary", sa.String(20), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("address", postgresql.JSONB(), nullable=True),
        sa.Column("emergency_contact", postgresql.JSONB(), nullable=True),
        sa.Column("allergies", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("chronic_conditions", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("current_medications", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("status", sa.String(20), default="active"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_patients_patient_id", "patients", ["patient_id"])
    op.create_index("idx_patients_phone", "patients", ["phone_primary"])

    # Visits table
    op.create_table(
        "visits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("visit_number", sa.String(20), nullable=False, unique=True),
        sa.Column(
            "patient_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("patients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "doctor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column(
            "visit_date",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("chief_complaint", sa.Text(), nullable=True),
        sa.Column("symptoms", postgresql.JSONB(), nullable=True),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("vitals", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(20), default="in_progress"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_visits_patient", "visits", ["patient_id"])
    op.create_index("idx_visits_doctor", "visits", ["doctor_id"])
    op.create_index("idx_visits_date", "visits", ["visit_date"])

    # Recordings table
    op.create_table(
        "recordings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "visit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("visits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "doctor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("audio_url", sa.String(500), nullable=False),
        sa.Column("audio_format", sa.String(20), default="wav"),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("language", sa.String(10), default="en"),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("transcript_segments", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_recordings_visit", "recordings", ["visit_id"])
    op.create_index("idx_recordings_status", "recordings", ["status"])

    # Prescriptions table
    op.create_table(
        "prescriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "visit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("visits.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("medications", postgresql.JSONB(), nullable=False, default=[]),
        sa.Column("injections", postgresql.JSONB(), nullable=True),
        sa.Column("investigations", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("follow_up_date", sa.Date(), nullable=True),
        sa.Column("follow_up_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_prescriptions_visit", "prescriptions", ["visit_id"])

    # Diet plans table
    op.create_table(
        "diet_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "visit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("visits.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("breakfast", postgresql.JSONB(), nullable=True),
        sa.Column("lunch", postgresql.JSONB(), nullable=True),
        sa.Column("dinner", postgresql.JSONB(), nullable=True),
        sa.Column("snacks", postgresql.JSONB(), nullable=True),
        sa.Column("foods_to_avoid", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("dietary_restrictions", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("hydration_advice", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_diet_plans_visit", "diet_plans", ["visit_id"])

    # Care instructions table
    op.create_table(
        "care_instructions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "visit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("visits.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "lifestyle_recommendations", postgresql.ARRAY(sa.String()), nullable=True
        ),
        sa.Column("exercise_plan", postgresql.JSONB(), nullable=True),
        sa.Column("sleep_recommendations", sa.Text(), nullable=True),
        sa.Column("stress_management", sa.Text(), nullable=True),
        sa.Column("warning_signs", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("when_to_seek_help", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("additional_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_care_instructions_visit", "care_instructions", ["visit_id"])

    # Reports table
    op.create_table(
        "reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("report_number", sa.String(20), nullable=False, unique=True),
        sa.Column(
            "visit_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("visits.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("report_type", sa.String(50), default="full"),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column("preview_url", sa.String(500), nullable=True),
        sa.Column("qr_code_data", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column("status", sa.String(20), default="generated"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_reports_visit", "reports", ["visit_id"])
    op.create_index("idx_reports_number", "reports", ["report_number"])


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("care_instructions")
    op.drop_table("diet_plans")
    op.drop_table("prescriptions")
    op.drop_table("recordings")
    op.drop_table("visits")
    op.drop_table("patients")
    op.drop_table("users")
