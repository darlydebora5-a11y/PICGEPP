import streamlit as st
import pandas as pd
import os
import re
import random
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
LOGO_PATH = "logo.png"

# --- LISTE DES FILIÈRES PAR ÉTABLISSEMENT (INSG, ITO, IST, IUSO, etc.) ---
LISTE_FILIERES = [
    "-- Choisir une filière --",
    "INSG : Comptabilité - Contrôle - Audit (CCA)",
    "INSG : Marketing et Commerce",
    "INSG : Gestion des Ressources Humaines",
    "INSG : Banque et Assurance",
    "IST : Génie Civil / BTP",
    "IST : Génie Électrique & Informatique Industrielle",
    "IST : Génie Mécanique & Productique",
    "IST : Maintenance Industrielle",
    "ITO : Technologies de l'Information",
    "ITO : Réseaux et Télécoms",
    "ITO : Cybersécurité",
    "IUSO : Management des Activités de Services",
    "IUSO : Sciences et Métiers de l'Ogooué",
    "ENSET : Enseignement Technique (F1, F2, F3, G...)",
    "ENS : Enseignement Général (Lettres, Sciences, HG)",
    "USS : Médecine / Santé",
    "USS : Sciences Infirmières / Sage-femme",
    "USTM : Mines et Géologie",
    "USTM : Polytechnique",
    "INSAB : Agronomie et Élevage",
    "INSAB : Eaux et Forêts"
]

# --- STYLE CSS (Bleu & Doré) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .main-title {{ color: #D4AF37 !important; font-size: 22px !important; font-weight: bold; text-align: center; text-transform: uppercase; margin-top: 10px; }}
    h2, h3, p, label, span {{ color: #D4AF37 !important; font-size: 14px; }}
    .urgent-box {{ background-color: #ffffff; padding: 8px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; }}
    .fiche-info {{ background: white; padding: 15px; border-radius: 10px; color: #003366 !important; border: 2px dashed #D4AF37; margin-bottom: 15px; }}
    [data-testid="stForm"] {{ border: 1px solid #D4AF37 !important; padding: 15px !important; border-radius: 15px; max-width: 380px; margin: auto; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; width: 100%; border-radius: 20px; border: none; }}
    input, .stSelectbox {{ background-color: #f0f2f6 !important; color: black !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTION LOGO CIRCULAIRE ---
def make_circle(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        size = (300, 300)
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output
    except: return None

# --- HEADER (LOGO & TITRE) ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    logo_circ = make_circle(LOGO_PATH)
    if logo_circ:
        st.image(logo_circ, width=110)
    else:
        st.markdown("<div style='width:110px; height:110px; border-radius:50%; background:#D4AF37; display:flex; align-items:center; justify-content:center; margin:auto; border:2px solid #D4AF37; color:#003366; font-weight:bold; font-size:24px;'>PIC</div>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)
st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscris-toi pour rester informé !</marquee></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL", "ADMIN"])

# --- ACCUEIL CANDIDAT ---
if menu == "ACCUEIL":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align: center; font-weight: bold;'>Identifie-toi pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp (ex: 077123456)")
            serie = st.selectbox("Série du BAC", ["-- Choisir --", "A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Établissement & Filière visée", LISTE_FILIERES)
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact and serie != "-- Choisir --" and filiere != "-- Choisir une filière --":
                    pd.DataFrame({
                        "Date": [datetime.now().strftime("%d/%m/%Y %H:%M")],
                        "Nom": [nom], "Contact": [contact], "Série": [serie], "Filière": [filiere]
                    }).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
                    st.session_state.auth = True
                    st.session_state.user = {"nom": nom, "contact": contact, "serie": serie, "filiere": filiere}
                    st.rerun()
                else:
                    st.error("Veuillez remplir tous les champs.")
    else:
        st.markdown(f"""<div class="fiche-info">
            <h4 style="color:#003366 !important; text-align:center;">📄 FICHE D'INFORMATION PICGEPP</h4>
            <p style="color:#003366 !important;"><b>Candidat :</b> {st.session_state.user['nom']}<br>
            <b>Choix :</b> {st.session_state.user['filiere']}<br>
            <b>Série :</b> {st.session_state.user['serie']}</p>
            <p style="color:#003366 !important;">✅ <b>Tes Avantages :</b><br>
            - Participation gratuite à un <b>concours blanc</b>.<br>
            - <b>Remise</b> sur l'achat du <b>Guide du Bachelier</b>.</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Se déconnecter"):
            st.session_state.auth = False
            st.rerun()

# --- ADMIN ---
elif menu == "ADMIN":
    pwd = st.text_input("Code Admin", type="password")
    if pwd == ADMIN_PASSWORD_MASTER:
        if os.path.exists(DB_FILE): 
            st.write("### Liste des Inscrits")
            st.dataframe(pd.read_csv(DB_FILE))
