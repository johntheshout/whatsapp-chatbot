from flask import Flask, request, render_template
import openai
import requests
import os
import fitz  # PyMuPDF
import sqlite3
from generate_pdf import create_client_pdf
from database import init_db, log_message

app = Flask(__name__)

# Charger les variables d'environnement (.env)
openai.api_key = os.getenv("OPENAI_API_KEY")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

# Créer la base de données au démarrage
init_db()

def send_whatsapp_message(to, message):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    data = {
        "From": TWILIO_PHONE,
        "To": to,
        "Body": message
    }
    auth = (TWILIO_SID, TWILIO_TOKEN)
    requests.post(url, data=data, auth=auth)

def load_pdf_context(phone_number):
    filepath = f"data/{phone_number}.pdf"
    if not os.path.exists(filepath):
        return "No data found for this client."
    with fitz.open(filepath) as doc:
        return "\n".join([page.get_text() for page in doc])

def ask_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Réponds comme un assistant professionnel du service client."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get('Body')
    sender = request.form.get('From')
    phone_number = sender.replace("whatsapp:", "").replace("+", "")

    pdf_context = load_pdf_context(phone_number)
    prompt = f"Données du client :\n{pdf_context}\n\nMessage reçu : {incoming_msg}\nRéponds de manière personnalisée :"
    reply = ask_chatgpt(prompt)
    send_whatsapp_message(sender, reply)

    log_message(phone_number, incoming_msg, reply)
    return "OK", 200

@app.route("/admin")
def admin():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT phone, last_message, last_response FROM clients")
    rows = c.fetchall()
    conn.close()
    return render_template("admin.html", messages=rows)

@app.route("/new-client", methods=["GET", "POST"])
def new_client():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        content = request.form["content"]
        create_client_pdf(phone, f"Nom : {name}\nTéléphone : {phone}\n{content}")
        return f"PDF créé pour {phone}"
    return render_template("new_client.html")

if __name__ == "__main__":
    app.run(debug=True)