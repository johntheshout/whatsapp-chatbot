from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def create_client_pdf(phone_number, client_data):
    filepath = f"data/{phone_number}.pdf"
    os.makedirs("data", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=A4)
    text = c.beginText(40, 800)

    for line in client_data.split("\n"):
        text.textLine(line)

    c.drawText(text)
    c.save()
    print(f"PDF créé pour {phone_number}")