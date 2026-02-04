"""Report generation service."""

import base64
import hashlib
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID

import qrcode
from jinja2 import Environment, FileSystemLoader
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.care_instructions import CareInstructions
from app.models.diet_plan import DietPlan
from app.models.patient import Patient
from app.models.prescription import Prescription
from app.models.report import Report
from app.models.user import User
from app.models.visit import Visit
from app.schemas.report import (
    CareInstructionsInfo,
    DietPlanInfo,
    DoctorInfo,
    ExercisePlanInfo,
    HospitalInfo,
    MealInfo,
    MedicationInfo,
    InjectionInfo,
    PatientInfo,
    PrescriptionInfo,
    ReportGenerateRequest,
    ReportTemplateContext,
)
from app.services.storage import get_storage_service


class ReportService:
    """Service for generating and managing reports."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_service()
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True,
        )

    async def generate_report(
        self,
        request: ReportGenerateRequest,
        doctor_id: UUID,
    ) -> Report:
        """Generate a report for a visit."""
        # Get visit with all related data
        visit = await self._get_visit_with_relations(request.visit_id)
        if not visit:
            raise NotFoundError(f"Visit {request.visit_id} not found")

        # Get doctor info
        doctor = await self._get_user(doctor_id)
        if not doctor:
            raise NotFoundError(f"Doctor {doctor_id} not found")

        # Generate report number
        report_number = await self._generate_report_number()

        # Build template context
        context = await self._build_template_context(
            visit=visit,
            doctor=doctor,
            report_number=report_number,
            include_sections=request.include_sections,
        )

        # Render HTML
        template_name = self._get_template_name(request.report_type)
        html_content = self._render_template(template_name, context)

        # Generate PDF
        pdf_bytes = self._generate_pdf(html_content)

        # Calculate checksum
        checksum = hashlib.sha256(pdf_bytes).hexdigest()

        # Save PDF to storage
        pdf_url = await self.storage.upload_report(
            pdf_bytes,
            f"{report_number}.pdf",
            content_type="application/pdf",
        )

        # Create report record
        report = Report(
            report_number=report_number,
            visit_id=request.visit_id,
            report_type=request.report_type,
            pdf_url=pdf_url,
            preview_url=pdf_url,  # Same for now, can be different for HTML preview
            qr_code_data=context.qr_code_url,
            checksum=checksum,
            status="generated",
            expires_at=datetime.utcnow() + timedelta(days=365),
        )

        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)

        return report

    async def get_report(self, report_id: UUID) -> Optional[Report]:
        """Get a report by ID."""
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def get_report_by_number(self, report_number: str) -> Optional[Report]:
        """Get a report by report number."""
        result = await self.db.execute(
            select(Report).where(Report.report_number == report_number)
        )
        return result.scalar_one_or_none()

    async def get_reports_by_visit(self, visit_id: UUID) -> list[Report]:
        """Get all reports for a visit."""
        result = await self.db.execute(
            select(Report)
            .where(Report.visit_id == visit_id)
            .order_by(Report.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_download_url(self, report_id: UUID) -> Optional[str]:
        """Get a presigned download URL for a report."""
        report = await self.get_report(report_id)
        if not report or not report.pdf_url:
            return None

        # Update downloaded_at
        report.downloaded_at = datetime.utcnow()
        report.status = "downloaded"
        await self.db.commit()

        return await self.storage.get_presigned_url(report.pdf_url, expiry_hours=1)

    async def get_preview_html(self, report_id: UUID) -> Optional[str]:
        """Get HTML preview for a report."""
        report = await self.get_report(report_id)
        if not report:
            return None

        # Get visit and rebuild context
        visit = await self._get_visit_with_relations(report.visit_id)
        if not visit:
            return None

        doctor = await self._get_user(visit.doctor_id)
        if not doctor:
            return None

        context = await self._build_template_context(
            visit=visit,
            doctor=doctor,
            report_number=report.report_number,
        )

        template_name = self._get_template_name(report.report_type)
        return self._render_template(template_name, context)

    async def delete_report(self, report_id: UUID) -> bool:
        """Delete a report."""
        report = await self.get_report(report_id)
        if not report:
            return False

        # Delete PDF from storage
        if report.pdf_url:
            await self.storage.delete_file(report.pdf_url)

        # Delete record
        await self.db.delete(report)
        await self.db.commit()

        return True

    async def _get_visit_with_relations(self, visit_id: UUID) -> Optional[Visit]:
        """Get visit with all related data."""
        result = await self.db.execute(
            select(Visit)
            .where(Visit.id == visit_id)
        )
        visit = result.scalar_one_or_none()

        if visit:
            # Load relations
            await self.db.refresh(visit, ["patient", "prescription", "diet_plan", "care_instructions"])

        return visit

    async def _get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _generate_report_number(self) -> str:
        """Generate a unique report number."""
        year = datetime.now().year

        result = await self.db.execute(
            select(Report)
            .where(Report.report_number.like(f"RPT-{year}-%"))
            .order_by(Report.report_number.desc())
            .limit(1)
        )
        last_report = result.scalar_one_or_none()

        if last_report:
            last_num = int(last_report.report_number.split("-")[-1])
            new_num = last_num + 1
        else:
            new_num = 1

        return f"RPT-{year}-{new_num:05d}"

    async def _build_template_context(
        self,
        visit: Visit,
        doctor: User,
        report_number: str,
        include_sections: Optional[list[str]] = None,
    ) -> ReportTemplateContext:
        """Build the template context from visit data."""
        patient = visit.patient

        # Build patient info
        patient_info = PatientInfo(
            id=patient.patient_id,
            name=patient.full_name,
            age=patient.age,
            gender=patient.gender,
            blood_group=patient.blood_group,
            phone=patient.phone_primary,
            weight_kg=visit.vitals.get("weight_kg") if visit.vitals else None,
            height_cm=visit.vitals.get("height_cm") if visit.vitals else None,
            bmi=visit.vitals.get("bmi") if visit.vitals else None,
            allergies=patient.allergies,
        )

        # Build doctor info
        doctor_info = DoctorInfo(
            name=doctor.name,
            qualification=doctor.qualification,
            registration_no=None,  # Could be added to User model
            department=None,
            phone=doctor.phone,
        )

        # Build hospital info (could be from settings or doctor's hospital)
        hospital_info = HospitalInfo(
            name=doctor.hospital_name or "MediNote Healthcare",
        )

        # Build prescription info
        prescription_info = None
        if visit.prescription:
            medications = []
            if visit.prescription.medications:
                for med in visit.prescription.medications:
                    medications.append(MedicationInfo(**med))

            injections = None
            if visit.prescription.injections:
                injections = [InjectionInfo(**inj) for inj in visit.prescription.injections]

            prescription_info = PrescriptionInfo(
                medications=medications,
                injections=injections,
                investigations=visit.prescription.investigations,
                follow_up_date=str(visit.prescription.follow_up_date) if visit.prescription.follow_up_date else None,
                follow_up_notes=visit.prescription.follow_up_notes,
            )

        # Build diet plan info
        diet_plan_info = None
        if visit.diet_plan:
            diet_plan_info = DietPlanInfo(
                breakfast=MealInfo(**visit.diet_plan.breakfast) if visit.diet_plan.breakfast else None,
                lunch=MealInfo(**visit.diet_plan.lunch) if visit.diet_plan.lunch else None,
                dinner=MealInfo(**visit.diet_plan.dinner) if visit.diet_plan.dinner else None,
                snacks=MealInfo(**visit.diet_plan.snacks) if visit.diet_plan.snacks else None,
                foods_to_avoid=visit.diet_plan.foods_to_avoid,
                hydration_advice=visit.diet_plan.hydration_advice,
                dietary_restrictions=visit.diet_plan.dietary_restrictions,
            )

        # Build care instructions info
        care_info = None
        if visit.care_instructions:
            exercise_plan = None
            if visit.care_instructions.exercise_plan:
                exercise_plan = ExercisePlanInfo(**visit.care_instructions.exercise_plan)

            care_info = CareInstructionsInfo(
                lifestyle_recommendations=visit.care_instructions.lifestyle_recommendations,
                exercise_plan=exercise_plan,
                sleep_recommendations=visit.care_instructions.sleep_recommendations,
                stress_management=visit.care_instructions.stress_management,
                warning_signs=visit.care_instructions.warning_signs,
                when_to_seek_help=visit.care_instructions.when_to_seek_help,
                additional_notes=visit.care_instructions.additional_notes,
            )

        # Generate QR code
        qr_url = f"https://verify.medinote.ai/reports/{report_number}"
        qr_base64 = self._generate_qr_code(qr_url)

        # Determine which sections to include
        include_prescription = True
        include_diet = True
        include_care = True

        if include_sections:
            include_prescription = "prescription" in include_sections
            include_diet = "diet" in include_sections
            include_care = "care" in include_sections

        return ReportTemplateContext(
            hospital=hospital_info,
            doctor=doctor_info,
            patient=patient_info,
            chief_complaint=visit.chief_complaint,
            diagnosis=visit.diagnosis,
            prescription=prescription_info,
            diet_plan=diet_plan_info,
            care_instructions=care_info,
            visit_date=visit.visit_date.strftime("%Y-%m-%d"),
            report_id=str(visit.id),
            report_number=report_number,
            qr_code_url=qr_url,
            qr_code_base64=qr_base64,
            include_prescription=include_prescription,
            include_diet=include_diet,
            include_care=include_care,
        )

    def _get_template_name(self, report_type: str) -> str:
        """Get template name for report type."""
        templates = {
            "full": "reports/full_report.html",
            "prescription_only": "reports/full_report.html",  # Use same for now
            "diet_only": "reports/full_report.html",
            "care_only": "reports/full_report.html",
        }
        return templates.get(report_type, "reports/full_report.html")

    def _render_template(self, template_name: str, context: ReportTemplateContext) -> str:
        """Render a Jinja2 template with context."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**context.model_dump())

    def _generate_pdf(self, html_content: str) -> bytes:
        """Generate PDF from HTML content using WeasyPrint."""
        try:
            from weasyprint import HTML, CSS

            css_path = self.templates_dir / "styles" / "report.css"
            css = CSS(filename=str(css_path)) if css_path.exists() else None

            stylesheets = [css] if css else []
            pdf = HTML(string=html_content).write_pdf(stylesheets=stylesheets)

            return pdf
        except ImportError:
            # Fallback: return HTML as bytes if WeasyPrint not available
            return html_content.encode("utf-8")
        except Exception as e:
            print(f"PDF generation error: {e}")
            return html_content.encode("utf-8")

    def _generate_qr_code(self, data: str) -> str:
        """Generate QR code as base64 encoded PNG."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode("utf-8")
