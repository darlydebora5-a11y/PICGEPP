import streamlit as st
import pandas as pd
import os
import re
import random
import base64
import qrcode
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageOps, ImageDraw
import csv

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
CHAT_FILE = "chat_history.csv"
LOGO_PATH = "logo.png"

ECOLES_PRIVEES = {
    "EM-GABON": "emg2026", "UNIVGA": "uvga2026", "IUSTE": "iuste2026", "AUI": "aui2026", "BBS": "bbs2026"
}

LISTE_FILIERES = [
    "-- Choisissez une filière --",
    "INSG : Gestion / Marketing / RH", "IST : Génie Civil / Industriel", 
    "ITO : Informatique / Réseaux", "IUSO : Management / Services", 
    "ENS / ENSET : Enseignement", "USS : Médecine / Santé", 
    "USTM : Mines / Polytechnique", "INSAB : Agronomie"
]

# --- STYLE CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .main-title {{ color: #D4AF37 !important; font-size: 26px !important; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 20px; }}
    h1, h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 10px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; }}
    .stats-bar {{ background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px solid #D4AF37; }}
    .fiche-info {{ background: white; padding: 20px; border-radius: 10px; color: #003366 !important; border: 2px dashed #D4AF37; margin-top: 15px; }}
    .fiche-info h4, .fiche-info p {{ color: #003366 !important; }}
    [data-testid="stForm"] {{ border: 1px solid #D4AF37 !important; padding: 20px !important; border-radius: 15px; max-width: 400px; margin: auto; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; width: 100%; border-radius: 20px; border: none; height: 3em; }}
    input, .stSelectbox {{ background-color: #f0f2f6 !important; color: black !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS DE SÉCURITÉ DONNÉES ---
def obtenir_stats():
    total = 0
    try:
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE, on_bad_lines='skip', sep=',')
            total = len(df)
    except: total = 0
    online = int(total * random.uniform(0.05, 0.12)) + random.randint(5, 15)
    return total, online

def enregistrer_candidat(nom, contact, serie, filiere, ecole):
    # Nettoyage des virgules pour éviter le plantage CSV
    nom = nom.replace(",", " ")
    data = {
        "Date": [datetime.now().strftime("%d/%m/%Y %H:%M")],
        "Nom": [nom], "Contact": [contact], "Série": [serie], 
        "Filière": [filiere], "Ecole_Cible": [ecole]
    }
    df = pd.DataFrame(data)
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
    else:
        df.to_csv(DB_FILE, mode='a', header=False, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)

# --- PDF & QR CODE ---
def generer_pdf(nom, contact, serie, filiere):
    pdf = FPDF(); pdf.add_page()
    pdf.set_font("Arial", 'B', 10); pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "PLATEFORME D'INFORMATION AUX CONCOURS DES GRANDES ECOLES PUBLIQUES & PRIVEES", ln=True, align='C')
    if os.path.exists(LOGO_PATH): pdf.image(LOGO_PATH, x=90, y=25, w=30); pdf.ln(35)
    else: pdf.ln(15)
    pdf.set_font("Arial", 'B', 16); pdf.cell(0, 10, "FICHE D'INFORMATION PICGEPP", ln=True, align='C'); pdf.ln(5)
    pdf.set_font("Arial", '', 12); pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Nom complet : {nom.upper()}", ln=True)
    pdf.cell(0, 10, f"Contact WhatsApp : {contact}", ln=True)
    pdf.cell(0, 10, f"Serie du BAC : {serie}", ln=True)
    pdf.cell(0, 10, f"Filiere visee : {filiere}", ln=True)
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "AVANTAGES DU CANDIDAT :", ln=True)
    pdf.set_font("Arial", '', 12); pdf.multi_cell(0, 10, "- Droit de participation GRATUITE a un concours blanc de preparation.\n- Remise speciale sur l'achat du Guide du Bachelier.")
    qr_data = f"PICGEPP | Nom: {nom} | Tel: {contact}"
    qr = qrcode.make(qr_data); qr.save("temp_qr.png"); pdf.image("temp_qr.png", x=85, y=pdf.get_y() + 10, w=40)
    return pdf.output(dest='S').encode('latin1')

# --- LOGO CIRCULAIRE ---
def make_circle(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        size = (300, 300); img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0); draw = ImageDraw.Draw(mask); draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask); return img
    except: return None

# --- HEADER ---
col1, col2, col3 = st.columns([1,1,1])
with col2:
    logo = make_circle(LOGO_PATH)
    if logo: st.image(logo, width=120)
    else: st.markdown("<div style='width:100px; height:100px; border-radius:50%; background:#D4AF37; margin:auto; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold; font-size:24px;'>PIC</div>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)
st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous pour rester informés !</marquee></div>', unsafe_allow_html=True)

total, online = obtenir_stats()
st.markdown(f'<div class="stats-bar"><span class="stat-item">👥 Inscrits : {total}</span><span class="stat-item">🟢 En ligne : {online}</span></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL", "ESPACE ÉCOLE", "ADMINISTRATION"])

if menu == "ACCUEIL":
    if 'auth' not in st.session_state: st.session_state.auth = False
    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align:center;'>Identifiez-vous pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Filière souhaitée", LISTE_FILIERES)
            choix = st.selectbox("Université privée d'intérêt", ["Aucun"] + list(ECOLES_PRIVEES.keys()))
            if st.form_submit_button("VALIDER"):
                if nom and contact and filiere != "-- Choisissez une filière --":
                    enregistrer_candidat(nom, contact, serie, filiere, choix)
                    st.session_state.auth = True; st.session_state.u = {"n":nom, "c":contact, "s":serie, "f":filiere}; st.rerun()
    else:
        st.markdown(f'<div class="fiche-info"><h4 style="text-align:center;">📄 FICHE D\'INFORMATION PICGEPP</h4><p><b>Nom :</b> {st.session_state.u["n"]}<br><b>Contact :</b> {st.session_state.u["c"]}</p><p>✅ Concours blanc gratuit + Remise Guide du Bachelier.</p></div>', unsafe_allow_html=True)
        pdf = generer_pdf(st.session_state.u['n'], st.session_state.u['c'], st.session_state.u['s'], st.session_state.u['f'])
        st.download_button("📥 Télécharger ma Fiche PDF", pdf, "Fiche_PICGEPP.pdf", "application/pdf")
        st.button("Déconnexion", on_click=lambda: st.session_state.update({"auth": False}))

elif menu == "ESPACE ÉCOLE":
    ecole = st.selectbox("École", list(ECOLES_PRIVEES.keys()))
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Accéder"):
        if ECOLES_PRIVEES.get(ecole) == pwd: st.session_state.ec = ecole
    if 'ec' in st.session_state:
        df = pd.read_csv(DB_FILE, on_bad_lines='skip')
        st.dataframe(df[df['Ecole_Cible'] == st.session_state.ec])

elif menu == "ADMINISTRATION":
    if st.text_input("Code Maître", type="password") == ADMIN_PASSWORD_MASTER:
        if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE, on_bad_lines='skip'))
