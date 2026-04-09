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
    
    /* CENTRAGE ABSOLU DU LOGO ET DU TITRE */
    .header-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        padding: 20px 0;
    }}
    
    .main-title {{
        color: #D4AF37 !important;
        font-size: 32px !important;
        font-weight: bold;
        text-transform: uppercase;
        line-height: 1.3;
        margin-top: 25px;
        border-bottom: 2px solid #D4AF37;
        padding-bottom: 15px;
        width: 90%;
        margin-left: auto;
        margin-right: auto;
    }}
    
    h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 10px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 20px; }}
    
    /* Cartes des Écoles */
    .school-card {{
        background: white; padding: 15px; border-radius: 12px; text-align: center;
        border: 2px solid #D4AF37; margin-bottom: 15px;
    }}
    .school-name {{ color: #003366 !important; font-weight: bold; font-size: 16px; margin-top: 8px; }}
    
    /* Espace Discussion */
    .chat-container {{
        background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 15px; border: 1px solid #D4AF37;
    }}
    .chat-msg-small {{ background: white; padding: 10px; border-radius: 8px; color: black !important; margin-bottom: 10px; font-size: 13px; border-left: 5px solid #D4AF37; }}
    
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

# --- HEADER (LOGO ET TITRE GÉANT) ---
# Utilisation de colonnes pour forcer le centrage du logo
_, col_logo_center, _ = st.columns([2, 1, 2])
with col_logo_center:
    logo_main = make_circle(LOGO_PLATEFORME, size=(200,200))
    if logo_main: 
        st.image(logo_main, use_container_width=True)
    else: 
        st.markdown("<div style='width:120px; height:120px; border-radius:50%; background:#D4AF37; margin:auto; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold; font-size:28px;'>PIC</div>", unsafe_allow_html=True)

# Titre centré via CSS
st.markdown('<div class="header-container"><h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1></div>', unsafe_allow_html=True)

# --- SESSION AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

# --- 1. PAGE D'INSCRIPTION ---
if not st.session_state.auth:
    st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous pour rester informés !</marquee></div>', unsafe_allow_html=True)
    
    _, col_form, _ = st.columns([1, 2, 1])
    with col_form:
        with st.form("inscription"):
            st.markdown("<p style='text-align:center; font-weight:bold;'>Identifiez-vous pour accéder à votre espace candidat</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp (ex: 077123456)")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Filière souhaitée", ["Génie Civil", "Informatique", "Santé", "Management", "Enseignement", "Agronomie"])
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact:
                    st.session_state.auth = True
                    st.session_state.u = {"n":nom, "c":contact, "s":serie, "f":filiere}
                    st.rerun()
                else: st.error("Veuillez remplir tous les champs.")

# --- 2. TABLEAU DE BORD (APRÈS VALIDATION) ---
else:
    # Top Bar : Bienvenue et Bouton PDF
    top1, top2 = st.columns([3, 1])
    with top1: st.markdown(f"### 👋 Ravi de vous voir, **{st.session_state.u['n']}**")
    with top2:
        st.button("📥 Télécharger ma Fiche") # Bouton simplifié pour l'exemple

    st.divider()

    # Layout : Infos à gauche (2/3), Discussion à droite (1/3)
    col_infos, col_chat = st.columns([2, 1])

    with col_infos:
        st.markdown("### 📢 Actualités & Concours Publics")
        # Grille des écoles
        grid = st.columns(2)
        ecoles = ["ENS", "IST", "INSG", "ENSET"]
        for i, ecole in enumerate(ecoles):
            with grid[i % 2]:
                st.markdown(f'<div class="school-card"><div class="school-name">{ecole}</div><p style="color:gray; font-size:12px;">Infos bientôt disponibles.</p></div>', unsafe_allow_html=True)

    with col_chat:
        st.markdown('<div class="chat-container">### 💬 Discussion</div>', unsafe_allow_html=True)
        msg = st.text_input("Posez votre question...", key="chat_input")
        if st.button("Envoyer ✈️") and msg:
            st.rerun()

    if st.sidebar.button("Déconnexion"):
        st.session_state.auth = False
        st.rerun()
