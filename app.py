import streamlit as st
import pandas as pd
import os
import random
import csv
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="wide", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
CHAT_FILE = "chat_history.csv"
LOGO_PLATEFORME = "logo.png"

ECOLES_PRIVEES = {
    "EM-GABON": "emg2026", "UNIVGA": "uvga2026", "IUSTE": "iuste2026", "AUI": "aui2026", "BBS": "bbs2026"
}

# --- STYLE CSS (Prestige & Mobile Friendly) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .header-bar {{ display: flex; align-items: center; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; margin-bottom: 20px; }}
    .main-title-small {{ color: #D4AF37 !important; font-size: 20px !important; font-weight: bold; text-transform: uppercase; margin-left: 15px; }}
    h1, h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 8px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; }}
    .school-card {{ background: white; padding: 10px; border-radius: 12px; text-align: center; border: 2px solid #D4AF37; margin-bottom: 10px; min-height: 140px; }}
    .school-name {{ color: #003366 !important; font-weight: bold; font-size: 12px; margin-top: 5px; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; border-radius: 15px; border: none; }}
    input, .stSelectbox {{ background-color: #f0f2f6 !important; color: black !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION LOGO ---
def make_small_circle(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        size = (150, 150)
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0); draw = ImageDraw.Draw(mask); draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask); return img
    except: return None

# --- BARRE DE NAVIGATION (SIDEBAR) ---
st.sidebar.markdown("### ⚙️ ACCÈS RÉSERVÉS")
espace_pro = st.sidebar.radio("Navigation :", ["ACCUEIL CANDIDAT", "ESPACE ÉCOLE PRIVÉE", "ADMINISTRATION"])

# --- HEADER (LOGO RÉDUIT ET TITRE) ---
st.markdown('<div class="header-bar">', unsafe_allow_html=True)
col_l, col_t = st.columns([1, 8])
with col_l:
    logo = make_small_circle(LOGO_PLATEFORME)
    if logo: st.image(logo, width=70)
with col_t:
    st.markdown('<div class="main-title-small">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIQUE ---

if espace_pro == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous !</marquee></div>', unsafe_allow_html=True)
        _, col_f, _ = st.columns([1, 2, 1])
        with col_f:
            with st.form("inscription"):
                nom = st.text_input("Nom complet")
                contact = st.text_input("WhatsApp")
                serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
                if st.form_submit_button("VALIDER"):
                    if nom and contact:
                        st.session_state.auth = True
                        st.session_state.u = {"n":nom, "c":contact, "s":serie}
                        pd.DataFrame({"Date":[datetime.now()], "Nom":[nom], "Contact":[contact], "Série":[serie]}).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
                        st.rerun()
    else:
        # Dashboard avec Logos Réels
        c_inf, c_dis = st.columns([2, 1])
        with c_inf:
            st.markdown("### 📢 Actualités des Écoles Publiques")
            ecoles = [
                {"id": "ENS", "img": "ens.png"}, {"id": "ENSET", "img": "enset.png"}, 
                {"id": "IST", "img": "ist.png"}, {"id": "INSG", "img": "insg.png"},
                {"id": "ITO", "img": "ito.png"}, {"id": "IUSO", "img": "iuso.png"},
                {"id": "USS", "img": "uss.png"}, {"id": "USTM", "img": "ustm.png"},
                {"id": "INSAB", "img": "insab.png"}
            ]
            grid = st.columns(3)
            for i, ecole in enumerate(ecoles):
                with grid[i % 3]:
                    st.markdown(f'<div class="school-card">', unsafe_allow_html=True)
                    if os.path.exists(ecole['img']): st.image(ecole['img'], width=60)
                    else: st.write(f"🏛️ {ecole['id']}")
                    st.markdown(f'<div class="school-name">{ecole["id"]}</div></div>', unsafe_allow_html=True)
        with c_dis:
            st.markdown("### 💬 Discussion")
            if st.button("Déconnexion"): st.session_state.auth = False; st.rerun()

elif espace_pro == "ESPACE ÉCOLE PRIVÉE":
    ecole = st.selectbox("Établissement", list(ECOLES_PRIVEES.keys()))
    if st.text_input("Mot de passe", type="password") == ECOLES_PRIVEES.get(ecole):
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE, on_bad_lines='skip', encoding='utf-8-sig')
            st.dataframe(df)

elif espace_pro == "ADMINISTRATION":
    if st.text_input("Code Maître", type="password") == ADMIN_PASSWORD_MASTER:
        st.success("Accès Administrateur validé")
        if os.path.exists(DB_FILE):
            # La correction ParserError est ici : on ignore les lignes cassées
            df = pd.read_csv(DB_FILE, on_bad_lines='skip', encoding='utf-8-sig')
            st.dataframe(df)
            if st.button("Réinitialiser Base (Attention)"):
                os.remove(DB_FILE); st.rerun()
