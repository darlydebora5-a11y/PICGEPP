import streamlit as st
import pandas as pd
import os
import re
import random
import csv
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="wide", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
LOGO_PLATEFORME = "logo.png"

# --- LISTE COMPLÈTE DES FILIÈRES GABONAISES ---
LISTE_FILIERES = [
    "INSG : Gestion / Marketing / RH", "IST : Génie Civil / Industriel", 
    "ITO : Informatique / Réseaux", "IUSO : Management / Services", 
    "ENS : Enseignement Général", "ENSET : Enseignement Technique", 
    "USS : Médecine / Santé", "USTM : Mines / Polytechnique", 
    "INSAB : Agronomie / Eaux et Forêts"
]

# --- STYLE CSS (Prestige Bleu & Doré) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .header-bar {{ display: flex; align-items: center; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; margin-bottom: 20px; }}
    .main-title-small {{ color: #D4AF37 !important; font-size: 18px !important; font-weight: bold; text-transform: uppercase; margin-left: 10px; }}
    h1, h2, h3, p, label, span {{ color: #D4AF37 !important; }}
    .urgent-box {{ background-color: #ffffff; padding: 8px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; }}
    .school-card {{ background: white; padding: 10px; border-radius: 12px; text-align: center; border: 2px solid #D4AF37; margin-bottom: 10px; }}
    .school-name {{ color: #003366 !important; font-weight: bold; font-size: 12px; }}
    [data-testid="stForm"] {{ border: 1px solid #D4AF37 !important; border-radius: 15px; padding: 20px; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; border-radius: 15px; border: none; width: 100%; }}
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

# --- NAVIGATION SIDEBAR ---
st.sidebar.markdown("### ⚙️ NAVIGATION")
espace_pro = st.sidebar.radio("Espace :", ["ACCUEIL CANDIDAT", "ESPACE ÉCOLE PRIVÉE", "ADMINISTRATION"])

# --- HEADER ---
st.markdown('<div class="header-bar">', unsafe_allow_html=True)
col_logo, col_text = st.columns([1, 4])
with col_logo:
    logo = make_small_circle(LOGO_PLATEFORME)
    if logo: st.image(logo, width=60)
with col_text:
    st.markdown('<div class="main-title-small">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIQUE ---
if espace_pro == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous !</marquee></div>', unsafe_allow_html=True)
        
        # FORMULAIRE COMPLET (SANS SIMPLIFICATION)
        with st.form("inscription_complete"):
            st.markdown("<h4 style='text-align:center;'>Identifiez-vous pour rejoindre la communauté</h4>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            prenom = st.text_input("Prénom")
            whatsapp = st.text_input("Numéro WhatsApp")
            
            c1, c2 = st.columns(2)
            with c1:
                nationalite = st.selectbox("Nationalité", ["Gabonaise", "Étrangère"])
                sexe = st.radio("Sexe", ["Masculin", "Féminin"], horizontal=True)
            with c2:
                serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
                filiere = st.selectbox("Filière souhaitée", LISTE_FILIERES)
            
            if st.form_submit_button("VALIDER ET ACCÉDER AUX INFOS"):
                if nom and prenom and whatsapp:
                    st.session_state.auth = True
                    st.session_state.u = {"n": nom, "p": prenom, "w": whatsapp, "s": serie, "f": filiere}
                    # Sauvegarde sécurisée pour éviter ParserError
                    new_data = pd.DataFrame({
                        "Date": [datetime.now().strftime("%d/%m/%Y %H:%M")],
                        "Nom": [nom], "Prenom": [prenom], "WhatsApp": [whatsapp],
                        "Nationalite": [nationalite], "Sexe": [sexe], 
                        "Serie": [serie], "Filiere": [filiere]
                    })
                    new_data.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, quoting=csv.QUOTE_ALL)
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs obligatoires.")
    else:
        # Dashboard Candidat avec Logos Réels
        st.markdown(f"### 👋 Bienvenue, {st.session_state.u['p']} {st.session_state.u['n']}")
        c_inf, c_dis = st.columns([2, 1])
        with c_inf:
            st.markdown("#### 📢 Actualités des Écoles Publiques")
            ecoles = ["ENS", "ENSET", "IST", "INSG", "ITO", "IUSO", "USS", "USTM", "INSAB"]
            grid = st.columns(3)
            for i, e in enumerate(ecoles):
                with grid[i % 3]:
                    st.markdown(f'<div class="school-card">', unsafe_allow_html=True)
                    img_path = f"{e.lower()}.png"
                    if os.path.exists(img_path): st.image(img_path, width=50)
                    st.markdown(f'<div class="school-name">{e}</div></div>', unsafe_allow_html=True)
        with c_dis:
            st.markdown("#### 💬 Discussion")
            st.info("Espace de discussion activé.")
            if st.button("Se déconnecter"): st.session_state.auth = False; st.rerun()

elif espace_pro == "ESPACE ÉCOLE PRIVÉE":
    st.markdown("### 🔑 Accès Établissement")
    # Logique de connexion école ici...

elif espace_pro == "ADMINISTRATION":
    pwd = st.text_input("Code Maître", type="password")
    if pwd == ADMIN_PASSWORD_MASTER:
        st.success("Accès Administrateur validé")
        if os.path.exists(DB_FILE):
            # Correction ParserError : ignore les lignes mal formées
            df = pd.read_csv(DB_FILE, on_bad_lines='skip', encoding='utf-8-sig')
            st.dataframe(df)
