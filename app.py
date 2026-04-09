import streamlit as st
import pandas as pd
import os
import re
import random
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

# Sécurité Admin & Écoles
ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
LOGO_PATH = "logo.png"

# Les 5 meilleures universités privées (Cloisonnement par mot de passe)
ECOLES_PRIVEES = {
    "EM-GABON": "emg2026",
    "UNIVGA": "uvga2026",
    "IUSTE": "iuste2026",
    "AUI": "aui2026",
    "BBS": "bbs2026"
}

# --- LISTE DES FILIÈRES ---
LISTE_FILIERES = [
    "-- Choisir une filière --",
    "INSG : Comptabilité / Marketing / RH",
    "IST : Génie Civil / BTP / Industriel",
    "ITO : Informatique / Réseaux / Télécoms",
    "IUSO : Management / Sciences de l'Ogooué",
    "ENSET : Enseignement Technique",
    "ENS : Enseignement Général",
    "USS : Médecine / Santé",
    "USTM : Mines / Polytechnique",
    "INSAB : Agronomie / Eaux et Forêts"
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

# --- HEADER ---
col1, col2, col3 = st.columns([1,2,1])
with col2:
    logo_circ = make_circle(LOGO_PATH)
    if logo_circ: st.image(logo_circ, width=110)
    else: st.markdown("<div style='width:110px; height:110px; border-radius:50%; background:#D4AF37; display:flex; align-items:center; justify-content:center; margin:auto; border:2px solid #D4AF37; color:#003366; font-weight:bold;'>PIC</div>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)
st.markdown('<div class="urgent-box"><marquee style="color:red; font-weight:bold;">Urgent : Concours des Grandes Écoles Publiques en vue... Inscris-toi pour rester informé !</marquee></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL CANDIDAT", "ESPACE ÉCOLE PRIVÉE", "SUPER ADMIN"])

# --- 1. ACCUEIL CANDIDAT ---
if menu == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align: center; font-weight: bold;'>Identifie-toi pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp")
            serie = st.selectbox("Série du BAC", ["-- Choisir --", "A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Filière visée", LISTE_FILIERES)
            choix_ecole = st.selectbox("Université privée d'intérêt (Facultatif)", ["Aucune"] + list(ECOLES_PRIVEES.keys()))
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact and serie != "-- Choisir --" and filiere != "-- Choisir une filière --":
                    pd.DataFrame({
                        "Date": [datetime.now().strftime("%d/%m/%Y %H:%M")],
                        "Nom": [nom], "Contact": [contact], "Série": [serie], "Filière": [filiere], "Ecole_Cible": [choix_ecole]
                    }).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
                    st.session_state.auth = True
                    st.session_state.user = {"nom": nom, "serie": serie, "filiere": filiere}
                    st.rerun()
                else: st.error("Champs invalides.")
    else:
        st.markdown(f"""<div class="fiche-info">
            <h4 style="color:#003366 !important; text-align:center;">📄 FICHE D'INFORMATION PICGEPP</h4>
            <p style="color:#003366 !important;"><b>Candidat :</b> {st.session_state.user['nom']}<br>
            <b>Filière :</b> {st.session_state.user['filiere']}<br><b>Série :</b> {st.session_state.user['serie']}</p>
            <p style="color:#003366 !important;">✅ <b>Tes Avantages :</b> Concours blanc gratuit + Remise Guide du Bachelier.</p>
        </div>""", unsafe_allow_html=True)
        st.button("Se déconnecter", on_click=lambda: st.session_state.update({"auth": False}))

# --- 2. ESPACE ÉCOLE PRIVÉE (CLOISONNÉ) ---
elif menu == "ESPACE ÉCOLE PRIVÉE":
    st.subheader("🔑 Connexion Partenaire")
    ecole = st.selectbox("Votre établissement", list(ECOLES_PRIVEES.keys()))
    pwd = st.text_input("Mot de passe", type="password")
    
    if st.button("Accéder aux Candidats"):
        if ECOLES_PRIVEES.get(ecole) == pwd:
            st.session_state.ecole_auth = ecole
        else: st.error("Identifiants incorrects.")

    if 'ecole_auth' in st.session_state:
        st.success(f"Espace : {st.session_state.ecole_auth}")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            # Filtre : L'école ne voit que les candidats qui l'ont choisie
            df_prive = df[df['Ecole_Cible'] == st.session_state.ecole_auth]
            st.dataframe(df_prive)
            st.download_button("Télécharger Excel", df_prive.to_csv(index=False), "candidats.csv")
        if st.button("Quitter"): del st.session_state.ecole_auth; st.rerun()

# --- 3. SUPER ADMIN ---
elif menu == "SUPER ADMIN":
    st.subheader("🛠 Contrôle Général")
    master_pwd = st.text_input("Code Maître", type="password")
    if master_pwd == ADMIN_PASSWORD_MASTER:
        st.success("Accès Autorisé")
        if os.path.exists(DB_FILE):
            df_all = pd.read_csv(DB_FILE)
            st.write("### Base de données complète")
            st.dataframe(df_all)
            st.write(f"Total inscrits : {len(df_all)}")
