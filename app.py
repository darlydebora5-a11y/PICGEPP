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

# --- STYLE CSS (Logo réduit et Menu à droite) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    
    /* En-tête avec logo réduit et titre */
    .header-bar {{
        display: flex;
        align-items: center;
        justify-content: flex-start;
        padding: 10px;
        border-bottom: 2px solid #D4AF37;
        margin-bottom: 20px;
    }}
    .small-logo {{
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: 2px solid #D4AF37;
        margin-right: 15px;
    }}
    .main-title-small {{
        color: #D4AF37 !important;
        font-size: 20px !important;
        font-weight: bold;
        text-transform: uppercase;
    }}

    /* Boutons coins droits */
    .nav-buttons {{
        position: absolute;
        top: 10px;
        right: 10px;
        display: flex;
        gap: 10px;
        z-index: 1000;
    }}

    h1, h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 8px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; }}
    .school-card {{ background: white; padding: 10px; border-radius: 12px; text-align: center; border: 2px solid #D4AF37; margin-bottom: 10px; }}
    .school-name {{ color: #003366 !important; font-weight: bold; font-size: 13px; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; border-radius: 15px; border: none; font-size: 12px; }}
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

# --- BARRE DE NAVIGATION (EN HAUT À DROITE DANS LA SIDEBAR POUR MOBILE) ---
st.sidebar.markdown("### ⚙️ ACCÈS RÉSERVÉS")
espace_pro = st.sidebar.radio("Navigation :", ["ACCUEIL CANDIDAT", "ESPACE ÉCOLE PRIVÉE", "ADMINISTRATION"])

# --- HEADER (LOGO RÉDUIT ET TITRE) ---
st.markdown('<div class="header-bar">', unsafe_allow_html=True)
c1, c2 = st.columns([1, 8])
with c1:
    logo = make_small_circle(LOGO_PLATEFORME)
    if logo: st.image(logo, width=60)
    else: st.markdown("<div style='width:50px; height:50px; border-radius:50%; background:#D4AF37;'></div>", unsafe_allow_html=True)
with c2:
    st.markdown('<div class="main-title-small">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIQUE DES ESPACES ---

# 1. ACCUEIL CANDIDAT
if espace_pro == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous !</marquee></div>', unsafe_allow_html=True)
        _, col_form, _ = st.columns([1, 2, 1])
        with col_form:
            with st.form("inscription"):
                st.markdown("<p style='text-align:center;'>Identifiez-vous pour rejoindre la communauté</p>", unsafe_allow_html=True)
                nom = st.text_input("Nom complet")
                contact = st.text_input("WhatsApp")
                serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
                filiere = st.selectbox("Filière visée", ["INSG", "IST", "ITO", "IUSO", "ENS", "ENSET", "USS", "USTM", "INSAB"])
                if st.form_submit_button("VALIDER"):
                    if nom and contact:
                        st.session_state.auth = True
                        st.session_state.u = {"n":nom, "c":contact, "s":serie, "f":filiere}
                        pd.DataFrame({"Date":[datetime.now()], "Nom":[nom], "Contact":[contact], "Série":[serie], "Filière":[filiere]}).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False)
                        st.rerun()
    else:
        # Dashboard Candidat
        col_inf, col_dis = st.columns([2, 1])
        with col_inf:
            st.markdown("### 📢 Actualités des Écoles")
            # Logos des écoles (ENS, IST, INSG...)
            grid = st.columns(3)
            ecoles = [{"id": "ENS", "logo": "ens.png"}, {"id": "IST", "logo": "ist.png"}, {"id": "INSG", "logo": "insg.png"}]
            for i, ecole in enumerate(ecoles):
                with grid[i]:
                    st.markdown(f'<div class="school-card">', unsafe_allow_html=True)
                    if os.path.exists(ecole['logo']): st.image(ecole['logo'], width=50)
                    st.markdown(f'<div class="school-name">{ecole["id"]}</div></div>', unsafe_allow_html=True)
        with col_dis:
            st.markdown("### 💬 Chat")
            if st.button("Déconnexion"): st.session_state.auth = False; st.rerun()

# 2. ESPACE ÉCOLE PRIVÉE
elif espace_pro == "ESPACE ÉCOLE PRIVÉE":
    st.markdown("### 🔑 ACCÈS PARTENAIRE")
    ecole = st.selectbox("Établissement", list(ECOLES_PRIVEES.keys()))
    if st.text_input("Mot de passe", type="password") == ECOLES_PRIVEES.get(ecole):
        st.success(f"Connecté à {ecole}")
        if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))

# 3. ADMINISTRATION
elif espace_pro == "ADMINISTRATION":
    if st.text_input("Code Maître", type="password") == ADMIN_PASSWORD_MASTER:
        st.success("Mode Maître Activé")
        if os.path.exists(DB_FILE): st.dataframe(pd.read_csv(DB_FILE))
