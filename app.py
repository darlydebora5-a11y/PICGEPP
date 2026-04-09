import streamlit as st
import pandas as pd
import os
import re
import random
import qrcode
import csv
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageOps, ImageDraw
from io import BytesIO

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="wide", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
CHAT_FILE = "chat_history.csv"
LOGO_PLATEFORME = "logo.png"

# --- STYLE CSS (Bleu, Doré et Mise en page Mobile/Web) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .main-title {{ color: #D4AF37 !important; font-size: 26px !important; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 5px; }}
    h1, h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 10px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; }}
    
    /* Grille des Écoles */
    .school-card {{
        background: white; padding: 10px; border-radius: 12px; text-align: center;
        border: 2px solid #D4AF37; margin-bottom: 15px; min-height: 150px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}
    .school-name {{ color: #003366 !important; font-weight: bold; font-size: 15px; margin-top: 5px; }}
    
    /* Chat compact à droite */
    .chat-container {{
        background: rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 15px; border: 1px solid #D4AF37;
    }}
    .chat-msg-small {{ background: white; padding: 8px; border-radius: 8px; color: black !important; margin-bottom: 8px; font-size: 12px; border-left: 4px solid #D4AF37; }}
    
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; border-radius: 20px; width: 100%; border: none; }}
    input, .stSelectbox {{ background-color: #f0f2f6 !important; color: black !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS TECHNIQUES ---
def make_circle(image_path, size=(300, 300)):
    try:
        img = Image.open(image_path).convert("RGBA")
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0); draw = ImageDraw.Draw(mask); draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask); return img
    except: return None

def generer_pdf_officiel(nom, contact, serie, filiere):
    pdf = FPDF(); pdf.add_page()
    pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "FICHE D'INFORMATION PICGEPP GABON", ln=True, align='C')
    pdf.ln(10); pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Nom complet : {nom.upper()}", ln=True)
    pdf.cell(0, 10, f"Contact : {contact}", ln=True)
    pdf.cell(0, 10, f"Série : {serie} | Filière visée : {filiere}", ln=True)
    pdf.ln(10); pdf.set_font("Arial", 'B', 12); pdf.cell(0, 10, "AVANTAGES :", ln=True)
    pdf.set_font("Arial", '', 12); pdf.multi_cell(0, 10, "- Concours blanc gratuit\n- Remise Guide du Bachelier")
    return pdf.output(dest='S').encode('latin1')

# --- EN-TÊTE ---
col_logo, col_titre = st.columns([1, 4])
with col_logo:
    logo_main = make_circle(LOGO_PLATEFORME, size=(150,150))
    if logo_main: st.image(logo_main, width=100)
with col_titre:
    st.markdown('<h1 class="main-title">PICGEPP GABON</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; font-size:12px; margin-top:-10px;">Informations aux Concours des Grandes Écoles Publiques & Privées</p>', unsafe_allow_html=True)

# --- SESSION AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 1. PAGE D'INSCRIPTION ---
if not st.session_state.auth:
    st.markdown('<div class="urgent-box"><marquee class="marquee-text"><span style="color:red;">Urgent :</span> <span style="color:black;">Concours des Grandes Écoles Publiques en vue... Inscrivez-vous pour rester informés !</span></marquee></div>', unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        with st.form("inscription"):
            st.markdown("<p style='text-align:center; font-weight:bold;'>Identifiez-vous pour accéder au tableau de bord</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp (ex: 077123456)")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Filière souhaitée", ["Génie Civil", "Informatique", "Santé", "Management", "Enseignement"])
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact:
                    st.session_state.auth = True
                    st.session_state.u = {"n":nom, "c":contact, "s":serie, "f":filiere}
                    st.rerun()
                else: st.error("Veuillez remplir les champs.")

# --- 2. TABLEAU DE BORD (APRÈS INSCRIPTION) ---
else:
    # Top Bar : Bienvenue et Bouton PDF
    top1, top2 = st.columns([3, 1])
    with top1: st.markdown(f"### 👋 Ravi de vous voir, **{st.session_state.u['n']}**")
    with top2:
        pdf_bytes = generer_pdf_officiel(st.session_state.u['n'], st.session_state.u['c'], st.session_state.u['s'], st.session_state.u['f'])
        st.download_button("📥 Télécharger ma Fiche", pdf_bytes, f"Fiche_{st.session_state.u['n']}.pdf", "application/pdf")

    st.divider()

    # Layout principal
    col_infos, col_chat = st.columns([2, 1])

    with col_infos:
        st.markdown("### 📢 Actualités & Concours Publics")
        
        # Liste des écoles avec logos GitHub
        # Assure-toi que ces fichiers existent : ens.png, ist.png, insg.png, enset.png
        ecoles = [
            {"id": "ENS", "logo": "ens.png", "msg": "Ouverture des dossiers le 12 mai."},
            {"id": "IST", "logo": "ist.png", "msg": "Épreuves de Maths disponibles."},
            {"id": "INSG", "logo": "insg.png", "msg": "Concours blanc le 20 avril."},
            {"id": "ENSET", "logo": "enset.png", "msg": "Dernier délai : 30 juin."}
        ]
        
        grid = st.columns(2)
        for i, ecole in enumerate(ecoles):
            with grid[i % 2]:
                st.markdown(f'<div class="school-card">', unsafe_allow_html=True)
                if os.path.exists(ecole['logo']):
                    st.image(ecole['logo'], width=60)
                else:
                    st.markdown(f"🏛️ **{ecole['id']}**")
                st.markdown(f'<div class="school-name">{ecole["id"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<p style="color:gray; font-size:11px;">{ecole["msg"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with col_chat:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown("### 💬 Discussion")
        msg = st.text_input("Un message ?", key="chat_input", label_visibility="collapsed", placeholder="Posez votre question...")
        if st.button("Envoyer ✈️") and msg:
            with open(CHAT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%H:%M')},{st.session_state.u['n']},{msg}\n")
            st.rerun()
        
        st.markdown("---")
        if os.path.exists(CHAT_FILE):
            try:
                df_chat = pd.read_csv(CHAT_FILE, names=["Heure", "User", "Texte"]).iloc[::-1]
                for _, row in df_chat.head(8).iterrows():
                    st.markdown(f'<div class="chat-msg-small"><b>{row["User"]}</b>: {row["Texte"]}</div>', unsafe_allow_html=True)
            except: st.write("Commencez la discussion !")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.sidebar.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()
