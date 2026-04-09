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

# --- STYLE CSS (Prestige Bleu & Doré) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    
    /* CENTRAGE DU HEADER */
    .header-container {{
        text-align: center;
        width: 100%;
        margin: auto;
    }}
    
    .main-title {{
        color: #D4AF37 !important;
        font-size: 30px !important;
        font-weight: bold;
        text-transform: uppercase;
        line-height: 1.2;
        margin-top: 20px;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 15px;
    }}
    
    h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 10px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 20px; }}
    
    /* Grille des Écoles Réelles */
    .school-card {{
        background: white; padding: 15px; border-radius: 12px; text-align: center;
        border: 2px solid #D4AF37; margin-bottom: 15px; min-height: 160px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }}
    .school-name {{ color: #003366 !important; font-weight: bold; font-size: 15px; margin-top: 8px; }}
    
    /* Chat compact */
    .chat-container {{
        background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 15px; border: 1px solid #D4AF37;
    }}
    .chat-msg-small {{ background: white; padding: 8px; border-radius: 8px; color: black !important; margin-bottom: 8px; font-size: 12px; border-left: 5px solid #D4AF37; }}
    
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; border-radius: 20px; width: 100%; height: 3em; border: none; }}
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

# --- HEADER (LOGO CENTRÉ ET TITRE GÉANT) ---
# Utilisation de 5 colonnes pour un centrage parfait du logo principal
c1, c2, c_center, c4, c5 = st.columns([1, 1, 2, 1, 1])
with c_center:
    logo_main = make_circle(LOGO_PLATEFORME, size=(200,200))
    if logo_main: st.image(logo_main, use_container_width=True)
    else: st.markdown("<div style='width:120px; height:120px; border-radius:50%; background:#D4AF37; margin:auto; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold; font-size:28px;'>PIC</div>", unsafe_allow_html=True)

st.markdown('<div class="header-container"><h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1></div>', unsafe_allow_html=True)

# --- SESSION AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 1. PAGE D'INSCRIPTION ---
if not st.session_state.auth:
    st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous pour rester informés !</marquee></div>', unsafe_allow_html=True)
    
    _, col_form, _ = st.columns([1, 2, 1])
    with col_form:
        with st.form("inscription"):
            st.markdown("<p style='text-align:center; font-weight:bold;'>Identifiez-vous pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp (ex: 077123456)")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Filière souhaitée", ["INSG", "IST", "ITO", "IUSO", "ENS", "ENSET", "USS", "USTM", "INSAB"])
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact:
                    st.session_state.auth = True
                    st.session_state.u = {"n":nom, "c":contact, "s":serie, "f":filiere}
                    st.rerun()
                else: st.error("Veuillez remplir tous les champs.")

# --- 2. TABLEAU DE BORD (APRÈS VALIDATION) ---
else:
    t1, t2 = st.columns([3, 1])
    with t1: st.markdown(f"### 👋 Bienvenue, **{st.session_state.u['n']}**")
    with t2:
        # Le bouton de téléchargement de la fiche PDF est ici
        st.button("📥 Télécharger ma Fiche")

    st.divider()

    col_infos, col_chat = st.columns([2, 1])

    with col_infos:
        st.markdown("### 📢 Actualités des Écoles Publiques")
        
        # Grille utilisant uniquement tes logos GitHub
        ecoles_reelles = [
            {"id": "ENS", "logo": "ens.png"}, {"id": "ENSET", "logo": "enset.png"},
            {"id": "IST", "logo": "ist.png"}, {"id": "INSG", "logo": "insg.png"},
            {"id": "ITO", "logo": "ito.png"}, {"id": "IUSO", "logo": "iuso.png"},
            {"id": "USS", "logo": "uss.png"}, {"id": "USTM", "logo": "ustm.png"},
            {"id": "INSAB", "logo": "insab.png"}
        ]
        
        grid = st.columns(3)
        for i, ecole in enumerate(ecoles_reelles):
            with grid[i % 3]:
                st.markdown(f'<div class="school-card">', unsafe_allow_html=True)
                if os.path.exists(ecole['logo']):
                    st.image(ecole['logo'], width=70)
                else:
                    st.markdown(f"🏛️ **{ecole['id']}**")
                st.markdown(f'<div class="school-name">{ecole["id"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with col_chat:
        st.markdown('<div class="chat-container">### 💬 Discussion</div>', unsafe_allow_html=True)
        msg = st.text_input("Message...", key="chat_input", label_visibility="collapsed")
        if st.button("Envoyer ✈️") and msg:
            with open(CHAT_FILE, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%H:%M')},{st.session_state.u['n']},{msg}\n")
            st.rerun()
        
        if os.path.exists(CHAT_FILE):
            try:
                df_chat = pd.read_csv(CHAT_FILE, names=["Heure", "User", "Texte"]).iloc[::-1]
                for _, row in df_chat.head(10).iterrows():
                    st.markdown(f'<div class="chat-msg-small"><b>{row["User"]}</b>: {row["Texte"]}</div>', unsafe_allow_html=True)
            except: st.write("Discutez avec les autres bacheliers.")

    if st.sidebar.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()
