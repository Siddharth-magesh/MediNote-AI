"""Report API endpoints."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import HTMLResponse, Response

from app.api.deps import CurrentUser, DBSession
from app.core.exceptions import NotFoundError
from app.schemas.report import (
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportListResponse,
    ReportResponse,
)
from app.services.report import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/generate", response_model=ReportGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    request: ReportGenerateRequest,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Generate a new report for a visit.

    **Request:**
    - **visit_id**: UUID of the visit
    - **report_type**: Type of report (full, prescription_only, diet_only, care_only)
    - **format**: Output format (pdf or html)
    - **include_sections**: Optional list of sections to include

    **Returns:**
    - Report ID and download/preview URLs
    """
    service = ReportService(db)

    try:
        report = await service.generate_report(request, current_user.id)

        return ReportGenerateResponse(
            report_id=report.id,
            report_number=report.report_number,
            download_url=f"/api/v1/reports/{report.id}/download",
            preview_url=f"/api/v1/reports/{report.id}/preview",
            expires_at=report.expires_at,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}",
        )


@router.get("", response_model=ReportListResponse)
async def list_reports(
    db: DBSession,
    current_user: CurrentUser,
    visit_id: Optional[UUID] = Query(None, description="Filter by visit ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List reports, optionally filtered by visit.
    """
    service = ReportService(db)

    if visit_id:
        reports = await service.get_reports_by_visit(visit_id)
        return ReportListResponse(
            results=reports,
            total=len(reports),
            skip=skip,
            limit=limit,
        )

    # TODO: Implement general listing with pagination
    return ReportListResponse(
        results=[],
        total=0,
        skip=skip,
        limit=limit,
    )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get a report by ID.
    """
    service = ReportService(db)
    report = await service.get_report(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )

    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get a download URL for a report PDF.

    Returns a presigned URL that expires in 1 hour.
    """
    service = ReportService(db)
    url = await service.get_download_url(report_id)

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found or has no PDF",
        )

    return {
        "download_url": url,
        "expires_in_seconds": 3600,
    }


@router.get("/{report_id}/preview", response_class=HTMLResponse)
async def preview_report(
    report_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Get HTML preview of a report.

    Returns the rendered HTML that can be displayed in a browser.
    """
    service = ReportService(db)
    html = await service.get_preview_html(report_id)

    if not html:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )

    return HTMLResponse(content=html)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Delete a report.
    """
    service = ReportService(db)
    deleted = await service.delete_report(report_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report {report_id} not found",
        )


@router.get("/verify/{report_number}")
async def verify_report(
    report_number: str,
    db: DBSession,
):
    """
    Verify a report by its report number.

    This endpoint is public (no auth required) for QR code verification.
    """
    service = ReportService(db)
    report = await service.get_report_by_number(report_number)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found or invalid",
        )

    return {
        "valid": True,
        "report_number": report.report_number,
        "report_type": report.report_type,
        "generated_at": report.created_at.isoformat(),
        "status": report.status,
    }


@router.post("/visit/{visit_id}/generate-all")
async def generate_all_reports_for_visit(
    visit_id: UUID,
    db: DBSession,
    current_user: CurrentUser,
):
    """
    Generate a full report for a visit.

    Convenience endpoint that generates a complete report with all sections.
    """
    request = ReportGenerateRequest(
        visit_id=visit_id,
        report_type="full",
        format="pdf",
    )

    service = ReportService(db)

    try:
        report = await service.generate_report(request, current_user.id)

        return {
            "report_id": str(report.id),
            "report_number": report.report_number,
            "download_url": f"/api/v1/reports/{report.id}/download",
            "preview_url": f"/api/v1/reports/{report.id}/preview",
        }
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
