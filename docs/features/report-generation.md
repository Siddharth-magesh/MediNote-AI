# Report Generation Feature

## Overview
Generate professional, print-ready medical reports from extracted conversation data.

## Report Types

### 1. Full Medical Report
Complete prescription with all extracted data including:
- Patient demographics
- Prescription details
- Diet plan
- Care instructions
- Doctor information

### 2. Prescription Only
Compact prescription slip with:
- Essential patient info
- Medications only
- Follow-up date

### 3. Diet Plan Only
Standalone dietary recommendations document.

### 4. Care Instructions
Patient take-home care guide.

## Report Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HEADER                                       │
│  ┌─────────────────────────────┐  ┌───────────────────────────────┐ │
│  │ Hospital/Clinic Logo        │  │ Doctor Information            │ │
│  │ Hospital Name               │  │ Name, Qualification           │ │
│  │ Address                     │  │ Registration Number           │ │
│  │ Contact                     │  │ Department                    │ │
│  └─────────────────────────────┘  └───────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────┤
│                      PATIENT INFORMATION                             │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Name: ________    Age: ___   Gender: ___   Blood Group: ___    ││
│  │ Contact: _______  Weight: ___ kg   Height: ___ cm   BMI: ___   ││
│  │ Patient ID: _______________   Date: _______________            ││
│  └─────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────┤
│                         PRESCRIPTION (Rx)                            │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ # │ Medicine Name    │ Dosage │ Timing  │ Duration │ Notes     ││
│  │───│──────────────────│────────│─────────│──────────│───────────││
│  │ 1 │ Paracetamol     │ 500mg  │ After   │ 5 days   │ If fever  ││
│  │   │                  │        │ meals   │          │           ││
│  │ 2 │ ...              │        │         │          │           ││
│  └─────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────┤
│                          DIET PLAN                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────────┐│
│  │  Breakfast   │ │    Lunch     │ │         Dinner               ││
│  │  7-9 AM      │ │   12-2 PM    │ │         7-9 PM               ││
│  │  - Item 1    │ │  - Item 1    │ │       - Item 1               ││
│  │  - Item 2    │ │  - Item 2    │ │       - Item 2               ││
│  └──────────────┘ └──────────────┘ └──────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────┤
│                      CARE INSTRUCTIONS                               │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ • Lifestyle recommendation 1                                    ││
│  │ • Exercise guideline                                            ││
│  │ • Warning signs to watch for                                    ││
│  └─────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────┤
│                          FOOTER                                      │
│  ┌──────────────────────┐            ┌──────────────────────────┐  │
│  │ Follow-up: 2 weeks   │            │ Doctor's Signature       │  │
│  │ QR Code for          │            │ ___________________      │  │
│  │ verification         │            │ Date: ______________     │  │
│  └──────────────────────┘            └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Template System

### Template Engine
Using Jinja2 for HTML templates + WeasyPrint for PDF conversion.

### Template Structure
```
templates/
├── base/
│   └── report_base.html       # Common layout
├── components/
│   ├── header.html            # Hospital/Doctor info
│   ├── patient_info.html      # Patient details block
│   ├── prescription.html      # Rx table
│   ├── diet_plan.html         # Diet section
│   ├── care_instructions.html # Care management
│   └── footer.html            # Signature, QR
├── reports/
│   ├── full_report.html       # Complete report
│   ├── prescription_only.html # Compact Rx
│   └── diet_only.html         # Diet plan only
└── styles/
    └── report.css             # Print-optimized CSS
```

### Template Variables
```python
template_context = {
    # Hospital/Clinic
    "hospital": {
        "name": "City Hospital",
        "address": "123 Medical Street",
        "phone": "+91-xxx-xxx-xxxx",
        "logo_url": "/static/logos/hospital.png"
    },

    # Doctor
    "doctor": {
        "name": "Dr. John Smith",
        "qualification": "MBBS, MD",
        "registration_no": "MCI-12345",
        "department": "General Medicine",
        "signature_url": "/static/signatures/dr_smith.png"
    },

    # Patient
    "patient": {
        "id": "PAT-2024-001",
        "name": "John Doe",
        "age": 40,
        "gender": "Male",
        # ... other fields
    },

    # Medical Data
    "prescription": {...},
    "diet_plan": {...},
    "care_instructions": {...},

    # Metadata
    "visit_date": "2024-01-15",
    "report_id": "RPT-xxx",
    "qr_data": "https://verify.medinote.ai/RPT-xxx"
}
```

## PDF Generation

### Method 1: WeasyPrint (Recommended)
```python
from weasyprint import HTML, CSS

def generate_pdf(template_name: str, context: dict) -> bytes:
    html_content = render_template(template_name, **context)

    css = CSS(filename='templates/styles/report.css')
    pdf = HTML(string=html_content).write_pdf(stylesheets=[css])

    return pdf
```

### Method 2: ReportLab (Alternative)
For more complex layouts or when HTML/CSS isn't sufficient.

### Page Settings
| Setting | Value |
|---------|-------|
| Page Size | A4 (210 x 297 mm) |
| Margins | 15mm all sides |
| Font | Open Sans / Roboto |
| Font Size | 10-12pt body, 14pt headers |

## API Endpoints

### Generate Report
```http
POST /api/v1/reports/generate
Content-Type: application/json

{
  "visit_id": "uuid",
  "report_type": "full",
  "format": "pdf",
  "include_sections": ["prescription", "diet", "care"]
}

Response:
{
  "report_id": "uuid",
  "download_url": "/api/v1/reports/download/{report_id}",
  "preview_url": "/api/v1/reports/preview/{report_id}",
  "expires_at": "2024-01-16T00:00:00Z"
}
```

### Download Report
```http
GET /api/v1/reports/download/{report_id}

Response: application/pdf
Content-Disposition: attachment; filename="prescription_PAT001_2024-01-15.pdf"
```

### Preview Report
```http
GET /api/v1/reports/preview/{report_id}

Response: text/html (rendered preview)
```

## QR Code Integration

### QR Code Content
```json
{
  "url": "https://verify.medinote.ai/reports/{report_id}",
  "data": {
    "report_id": "RPT-xxx",
    "patient_id": "PAT-xxx",
    "doctor_id": "DOC-xxx",
    "issued_date": "2024-01-15",
    "checksum": "sha256_hash"
  }
}
```

### Verification Page
Scanning QR code shows:
- Report authenticity status
- Issuing doctor details
- Issue date and time
- Tamper detection

## Customization Options

### Doctor-Level Customization
- Signature upload
- Personal letterhead
- Default prescription templates
- Favorite medications

### Hospital-Level Customization
- Logo and branding
- Header/footer content
- Report numbering format
- Watermark

## Storage & Retention

| Item | Retention Period |
|------|------------------|
| Generated PDF | 1 year |
| Report metadata | 7 years |
| Preview cache | 24 hours |

## Performance

| Metric | Target |
|--------|--------|
| PDF generation time | < 3 seconds |
| Download start | < 1 second |
| Concurrent generations | 50/minute |

## Testing Checklist

- [ ] All template sections render correctly
- [ ] PDF formatting matches design
- [ ] Fonts render properly
- [ ] QR code is scannable
- [ ] Multi-page reports paginate correctly
- [ ] Special characters handled
- [ ] Empty sections handled gracefully
- [ ] Download works in all browsers
- [ ] Print output matches preview

## Related Documentation
- [AI Data Extraction](./ai-extraction.md)
- [Template Customization](../frontend/templates.md)
- [File Storage](../backend/file-storage.md)
