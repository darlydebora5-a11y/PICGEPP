import streamlit as st
import pandas as pd
import os
import re
import random
from datetime import datetime
import base64
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
ECOLES_PRIVEES = {"EM-GABON": "emg2026", "UNIVGA": "uvga2026", "IUSTE": "iuste2026", "AUI": "aui2026", "BBS": "bbs2026"}

# --- STYLE CSS (Bleu & Doré) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .circular-logo-div {{ width: 120px; height: 120px; border-radius: 50%; border: 3px solid #D4AF37; background-color: #D4AF37; display: flex; justify-content: center; align-items: center; margin: 0 auto 15px auto; overflow: hidden; }}
    .main-title {{ color: #D4AF37 !important; font-size: 24px !important; font-weight: bold; text-align: center; text-transform: uppercase; }}
    h2, h3, p, label, span {{ color: #D4AF37 !important; font-size: 14px; }}
    .urgent-box {{ background-color: #ffffff; padding: 8px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; }}
    .fiche-info {{ background: white; padding: 15px; border-radius: 10px; color: #003366 !important; border: 2px dashed #D4AF37; margin-bottom: 15px; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; width: 100%; border-radius: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION GÉNÉRATION PDF ---
def generer_pdf(nom, serie):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "FICHE D'INFORMATION PICGEPP", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Candidat : {nom}", ln=True)
    pdf.cell(200, 10, f"Serie : {serie}", ln=True)
    pdf.cell(200, 10, f"Date : {datetime.now().strftime('%d/%m/%Y')}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "AVANTAGES ACQUIS :", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, "- Participation gratuite a un concours blanc de preparation.\n- Remise speciale sur l'achat du Guide du Bachelier (Epreuves + Corrections).")
    return pdf.output(dest='S').encode('latin1')

# --- HEADER ---
st.markdown('<div class="circular-logo-div"><span style="font-size:30px; color:#003366;">PIC</span></div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)

# --- BANDE DÉROULANTE ---
st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscris-toi pour rester informé !</marquee></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL", "ESPACE ÉCOLE", "ADMIN"])

# --- ACCUEIL ---
if menu == "ACCUEIL":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align: center;'>Identifie-toi pour rejoindre la communauté</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact:
                    pd.DataFrame({"Nom":[nom], "Contact":[contact], "Série":[serie]}).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                    st.session_state.auth = True
                    st.session_state.user = {"nom": nom, "serie": serie}
                    st.rerun()
    else:
        # AFFICHAGE DE LA FICHE
        st.markdown(f"""<div class="fiche-info">
            <h4 style="color:#003366 !important; text-align:center;">📄 FICHE D'INFORMATION PICGEPP</h4>
            <p style="color:#003366 !important;"><b>Nom :</b> {st.session_state.user['nom']}<br><b>Série :</b> {st.session_state.user['serie']}</p>
            <p style="color:#003366 !important;">✅ <b>Avantages :</b> Concours blanc gratuit + Remise Guide du Bachelier.</p>
        </div>""", unsafe_allow_html=True)
        
        # BOUTON TÉLÉCHARGEMENT PDF
        pdf_data = generer_pdf(st.session_state.user['nom'], st.session_state.user['serie'])
        st.download_button(label="📥 Télécharger ma Fiche en PDF", data=pdf_data, file_name=f"Fiche_PICGEPP_{st.session_state.user['nom']}.pdf", mime="application/pdf")
        
        if st.button("Se déconnecter"):
            st.session_state.auth = False
            st.rerun()

# --- ADMIN ---
elif menu == "ADMIN":
    pwd = st.text_input("Code Admin", type="password")
    if pwd == ADMIN_PASSWORD_MASTER:
        if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
