import streamlit as st
import pandas as pd
import os
import re
import random
from datetime import datetime
from fpdf import FPDF
import qrcode
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
LOGO_PATH = "logo.png" # Ton fichier doit s'appeler exactement comme ça

# --- STYLE CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .main-title {{ color: #D4AF37 !important; font-size: 22px !important; font-weight: bold; text-align: center; text-transform: uppercase; margin-top: 10px; }}
    h2, h3, p, label, span {{ color: #D4AF37 !important; font-size: 14px; }}
    .urgent-box {{ background-color: #ffffff; padding: 8px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; }}
    .fiche-info {{ background: white; padding: 15px; border-radius: 10px; color: #003366 !important; border: 2px dashed #D4AF37; margin-bottom: 15px; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; width: 100%; border-radius: 20px; }}
    /* Style pour centrer le logo */
    [data-testid="stImage"] {{ display: flex; justify-content: center; margin: 0 auto; border-radius: 50%; border: 3px solid #D4AF37; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION GÉNÉRATION PDF AVEC LOGO ET QR CODE ---
def generer_pdf_complet(nom, contact, serie):
    pdf = FPDF()
    pdf.add_page()
    
    # 1. En-tête avec Nom de la plateforme
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Plateforme d'Information aux Concours des Grandes Ecoles Publiques & Privees", ln=True, align='C')
    
    # 2. Ajout du Logo dans le PDF (si existe)
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=90, y=25, w=30)
        pdf.ln(35)
    else:
        pdf.ln(10)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FICHE D'INFORMATION PICGEPP", ln=True, align='C')
    pdf.ln(5)
    
    # 3. Informations Candidat
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Nom complet : {nom}", ln=True)
    pdf.cell(0, 10, f"Contact WhatsApp : {contact}", ln=True)
    pdf.cell(0, 10, f"Serie du BAC : {serie}", ln=True)
    pdf.cell(0, 10, f"Date d'emission : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "AVANTAGES DU CANDIDAT :", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, "- Participation GRATUITE a un concours blanc de preparation.\n- Remise speciale sur l'achat du Guide du Bachelier (Epreuves + Corrections).")
    
    # 4. Génération du QR Code
    qr_data = f"Candidat: {nom} | Tel: {contact} | PICGEPP GABON"
    qr = qrcode.make(qr_data)
    qr_path = "temp_qr.png"
    qr.save(qr_path)
    
    # 5. Insertion du QR Code en bas
    pdf.image(qr_path, x=85, y=pdf.get_y() + 10, w=40)
    
    return pdf.output(dest='S').encode('latin1')

# --- LOGO ET TITRE ---
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=120)
else:
    st.markdown("<div style='text-align:center; color:#D4AF37;'>[Logo manquant : déposez logo.png dans le dossier]</div>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)

# --- BANDE DÉROULANTE ---
st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscris-toi pour rester informé !</marquee></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL", "ADMIN"])

# --- ACCUEIL ---
if menu == "ACCUEIL":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align: center;'>Identifie-toi pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp (ex: 077123456)")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact:
                    pd.DataFrame({"Nom":[nom], "Contact":[contact], "Série":[serie]}).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                    st.session_state.auth = True
                    st.session_state.user = {"nom": nom, "contact": contact, "serie": serie}
                    st.rerun()
    else:
        st.markdown(f"""<div class="fiche-info">
            <h4 style="color:#003366 !important; text-align:center;">📄 FICHE D'INFORMATION PICGEPP</h4>
            <p style="color:#003366 !important;"><b>Nom :</b> {st.session_state.user['nom']}<br>
            <b>Contact :</b> {st.session_state.user['contact']}<br>
            <b>Série :</b> {st.session_state.user['serie']}</p>
            <p style="color:#003366 !important;">✅ <b>Avantages :</b> Concours blanc gratuit + Remise Guide du Bachelier.</p>
        </div>""", unsafe_allow_html=True)
        
        # Bouton PDF
        pdf_bytes = generer_pdf_complet(st.session_state.user['nom'], st.session_state.user['contact'], st.session_state.user['serie'])
        st.download_button(label="📥 Télécharger ma Fiche (PDF)", data=pdf_bytes, file_name=f"Fiche_PICGEPP_{st.session_state.user['nom']}.pdf", mime="application/pdf")
        
        if st.button("Se déconnecter"):
            st.session_state.auth = False
            st.rerun()

# --- ADMIN ---
elif menu == "ADMIN":
    pwd = st.text_input("Code Admin", type="password")
    if pwd == ADMIN_PASSWORD_MASTER:
        if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
