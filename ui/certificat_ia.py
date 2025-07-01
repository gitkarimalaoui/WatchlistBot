from datetime import datetime
import io
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


def generate_certificate(name: str, score: int) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(300, 700, "Certificat de Formation IA")
    c.setFont("Helvetica", 14)
    c.drawCentredString(300, 650, f"Décerné à {name}")
    c.drawCentredString(300, 620, f"Score : {score}/30")
    c.drawCentredString(300, 590, f"Date : {datetime.now().date().isoformat()}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
