import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from fpdf import FPDF
import qrcode
from PIL import Image, ImageOps, ImageDraw
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
LOGO_PATH = "logo.png"

ECOLES_PRIVEES = {
    "EM-GABON": "emg2026", "UNIVGA": "uvga2026", "IUSTE": "iuste2026", "AUI": "aui2026", "BBS": "bbs2026"
}

LISTE_FILIERES = [
    "-- Choisir une filière --",
    "INSG : Gestion / Marketing", "IST : Génie Civil / Industriel", 
    "ITO : Informatique / Réseaux", "IUSO : Management", 
    "ENS / ENSET : Enseignement", "USS : Médecine / Santé", 
    "USTM : Mines / Polytechnique", "INSAB : Agronomie"
]

# --- STYLE CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .main-title {{ color: #D4AF37 !important; font-size: 22px !important; font-weight: bold; text-align: center; text-transform: uppercase; }}
    h1, h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 8px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; }}
    .fiche-info {{ background: white; padding: 20px; border-radius: 10px; color: #003366 !important; border: 2px dashed #D4AF37; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; border-radius: 20px; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS ---
def make_circle(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        size = (300, 300)
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0); draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask)
        return img
    except: return None

def generer_pdf_officiel(nom, contact, serie, filiere):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête : Nom plateforme
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "PLATEFORME D'INFORMATION AUX CONCOURS DES GRANDES ECOLES PUBLIQUES & PRIVEES", ln=True, align='C')
    
    # Logo
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=90, y=25, w=30)
        pdf.ln(35)
    else: pdf.ln(15)

    # Titre Fiche
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FICHE D'INFORMATION PICGEPP", ln=True, align='C')
    pdf.ln(5)
    
    # Infos Candidat
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Nom complet : {nom.upper()}", ln=True)
    pdf.cell(0, 10, f"Contact WhatsApp : {contact}", ln=True)
    pdf.cell(0, 10, f"Serie du BAC : {serie}", ln=True)
    pdf.cell(0, 10, f"Filiere visee : {filiere}", ln=True)
    pdf.cell(0, 10, f"Date d'emission : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "AVANTAGES DU CANDIDAT :", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, "- Droit de participation GRATUITE a un concours blanc de preparation.\n- Remise speciale sur l'achat du Guide du Bachelier (Anciennes epreuves + Corrections).")
    
    # QR Code
    qr_data = f"PICGEPP GABON | Candidat: {nom} | Tel: {contact}"
    qr = qrcode.make(qr_data)
    qr_path = "temp_qr.png"
    qr.save(qr_path)
    pdf.image(qr_path, x=85, y=pdf.get_y() + 10, w=40)
    
    return pdf.output(dest='S').encode('latin1')

# --- LOGO ET TITRE ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    logo_circ = make_circle(LOGO_PATH)
    if logo_circ: st.image(logo_circ, width=120)
    else: st.markdown("<div style='width:100px; height:100px; border-radius:50%; background:#D4AF37; margin:auto; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold;'>PIC</div>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)
st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscris-toi pour rester informé !</marquee></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL CANDIDAT", "ESPACE ÉCOLE PRIVÉE", "SUPER ADMIN"])

# --- LOGIQUE ---
if menu == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align:center;'>Identifie-toi pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("Contact WhatsApp")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Filière souhaitée", LISTE_FILIERES)
            choix_ecole = st.selectbox("École privée d'intérêt (Facultatif)", ["Aucune"] + list(ECOLES_PRIVEES.keys()))
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact and filiere != "-- Choisir une filière --":
                    pd.DataFrame({"Date":[datetime.now()], "Nom":[nom], "Contact":[contact], "Série":[serie], "Filière":[filiere], "Ecole_Cible":[choix_ecole]}).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                    st.session_state.auth = True
                    st.session_state.user = {"nom":nom, "contact":contact, "serie":serie, "filiere":filiere}
                    st.rerun()
    else:
        st.markdown(f"""<div class="fiche-info">
            <h4 style="color:#003366 !important; text-align:center;">📄 FICHE D'INFORMATION PICGEPP</h4>
            <p style="color:#003366 !important;"><b>Candidat :</b> {st.session_state.user['nom']}<br><b>Contact :</b> {st.session_state.user['contact']}<br><b>Série :</b> {st.session_state.user['serie']}</p>
            <p style="color:#003366 !important;">✅ <b>Avantages :</b> Concours blanc gratuit + Remise Guide du Bachelier.</p>
        </div>""", unsafe_allow_html=True)
        
        pdf_bytes = generer_pdf_officiel(st.session_state.user['nom'], st.session_state.user['contact'], st.session_state.user['serie'], st.session_state.user['filiere'])
        st.download_button("📥 Télécharger ma Fiche en PDF", data=pdf_bytes, file_name=f"Fiche_PICGEPP_{st.session_state.user['nom']}.pdf", mime="application/pdf")
        st.button("Déconnexion", on_click=lambda: st.session_state.update({"auth": False}))

elif menu == "ESPACE ÉCOLE PRIVÉE":
    ecole = st.selectbox("Établissement", list(ECOLES_PRIVEES.keys()))
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Accéder"):
        if ECOLES_PRIVEES.get(ecole) == pwd: st.session_state.ecole_auth = ecole
    if 'ecole_auth' in st.session_state:
        df = pd.read_csv(DB_FILE)
        st.dataframe(df[df['Ecole_Cible'] == st.session_state.ecole_auth])

elif menu == "SUPER ADMIN":
    if st.text_input("Code Maître", type="password") == ADMIN_PASSWORD_MASTER:
        if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
