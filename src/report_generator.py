from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def _risk_from_probability(probability):
    if probability >= 0.8:
        return "HIGH"
    if probability >= 0.5:
        return "MODERATE"
    return "LOW"


def generate_report(probability):
    risk_level = _risk_from_probability(probability)
    probability_pct = f"{probability * 100:.1f}%"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    if risk_level == "HIGH":
        findings = (
            "Dense focal-to-lobar air-space opacities are present, with pattern suggestive "
            "of active infectious consolidation."
        )
        impression = "High likelihood of pneumonia."
        recommendations = [
            "Urgent clinical correlation with vitals, oxygen saturation, and inflammatory markers.",
            "Consider immediate empiric therapy per local protocol and physician judgment.",
            "Short-interval follow-up chest imaging if clinically indicated.",
        ]
    elif risk_level == "MODERATE":
        findings = (
            "Patchy bilateral/interstitial opacities are seen; findings are suspicious but not "
            "fully specific for pneumonia."
        )
        impression = "Intermediate likelihood of pneumonia."
        recommendations = [
            "Correlate with symptoms, examination findings, and laboratory work-up.",
            "Consider repeat imaging in 24-48 hours if symptoms progress.",
            "Escalate care if respiratory status worsens.",
        ]
    else:
        findings = (
            "No focal dense consolidation is identified. Mild non-specific background changes "
            "may be present."
        )
        impression = "Low likelihood of pneumonia."
        recommendations = [
            "Continue routine clinical assessment and symptom-based management.",
            "Re-image only if persistent or worsening respiratory symptoms.",
            "Use physician review for final diagnosis and treatment planning.",
        ]

    return {
        "generated_at": generated_at,
        "probability": probability,
        "probability_pct": probability_pct,
        "risk_level": risk_level,
        "findings": findings,
        "impression": impression,
        "recommendations": recommendations,
        "limitations": (
            "AI output is decision support only and may be affected by image quality, positioning, "
            "and domain shift."
        ),
        "disclaimer": "Final diagnosis must be made by a licensed clinician.",
    }


def format_report_markdown(report_data):
    rec_lines = "\n".join(
        [f"- {item}" for item in report_data["recommendations"]]
    )
    return f"""## AI Chest X-ray Report

**Generated:** {report_data['generated_at']}  
**Pneumonia Probability:** {report_data['probability_pct']}  
**Risk Level:** {report_data['risk_level']}

### Findings
{report_data['findings']}

### Impression
{report_data['impression']}

### Recommended Next Steps
{rec_lines}

### Limitations
{report_data['limitations']}

### Clinical Disclaimer
{report_data['disclaimer']}
"""


def _draw_wrapped_text(pdf, text, x, y, max_width, line_height):
    words = text.split()
    current_line = ""
    lines = []

    for word in words:
        trial = f"{current_line} {word}".strip()
        if pdf.stringWidth(trial, "Helvetica", 11) <= max_width:
            current_line = trial
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    for line in lines:
        pdf.drawString(x, y, line)
        y -= line_height

    return y


def create_pdf_report(report_data):
    with NamedTemporaryFile(delete=False, suffix=".pdf", prefix="chexnet_report_") as tmp:
        pdf_path = Path(tmp.name)

    pdf = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    margin = 18 * mm
    y = height - margin
    max_width = width - 2 * margin

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(margin, y, "CheXNet AI Report")
    y -= 14 * mm

    pdf.setFont("Helvetica", 11)
    y = _draw_wrapped_text(
        pdf,
        f"Generated: {report_data['generated_at']}",
        margin,
        y,
        max_width,
        14,
    )
    y = _draw_wrapped_text(
        pdf,
        f"Pneumonia Probability: {report_data['probability_pct']}",
        margin,
        y,
        max_width,
        14,
    )
    y = _draw_wrapped_text(
        pdf,
        f"Risk Level: {report_data['risk_level']}",
        margin,
        y,
        max_width,
        14,
    )
    y -= 6

    sections = [
        ("Findings", report_data["findings"]),
        ("Impression", report_data["impression"]),
        (
            "Recommended Next Steps",
            " ".join([f"{idx + 1}. {rec}" for idx, rec in enumerate(report_data["recommendations"])]),
        ),
        ("Limitations", report_data["limitations"]),
        ("Clinical Disclaimer", report_data["disclaimer"]),
    ]

    for title, body in sections:
        if y < margin + 45:
            pdf.showPage()
            y = height - margin
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(margin, y, title)
        y -= 16
        pdf.setFont("Helvetica", 11)
        y = _draw_wrapped_text(pdf, body, margin, y, max_width, 14)
        y -= 8

    pdf.save()
    return str(pdf_path)