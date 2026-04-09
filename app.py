import streamlit as st
import pandas as pd
import os
import re
import random
import base64
import qrcode
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageOps, ImageDraw
from io import BytesIO

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

# --- SÉCURITÉ ET BASES DE DONNÉES ---
ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
CHAT_FILE = "chat_history.csv"
LOGO_PATH = "logo.png"

# Établissements Privés Partenaires
ECOLES_PRIVEES = {
    "EM-GABON": "emg2026",
    "UNIVGA": "uvga2026",
    "IUSTE": "iuste2026",
    "AUI": "aui2026",
    "BBS": "bbs2026"
}

# Filières Officielles du Programme Gabonais
LISTE_FILIERES = [
    "-- Choisissez une filière --",
    "INSG : Comptabilité - Contrôle - Audit",
    "INSG : Marketing / Commerce / RH",
    "IST : Génie Civil / Bâtiment et Travaux Publics",
    "IST : Génie Électrique / Informatique Industrielle",
    "IST : Génie Mécanique / Productique",
    "ITO : Technologies de l'Information / Réseaux",
    "IUSO : Management des Activités de Services",
    "ENSET : Enseignement Technique et Professionnel",
    "ENS : Enseignement Secondaire (Général)",
    "USS : Médecine / Pharmacie / Maïeutique",
    "USTM : Mines et Géologie / Polytechnique",
    "INSAB : Agronomie / Élevage / Eaux et Forêts"
]

# --- STYLE CSS PERSONNALISÉ (Bleu Nuit & Doré) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    .main-title {{ color: #D4AF37 !important; font-size: 26px !important; font-weight: bold; text-align: center; text-transform: uppercase; margin-bottom: 20px; line-height: 1.2; }}
    h1, h2, h3, p, label, span {{ color: #D4AF37 !important; font-family: 'Arial', sans-serif; }}
    .urgent-box {{ background-color: #ffffff; padding: 10px; border-radius: 5px; text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; }}
    .marquee-text {{ color: #ff0000 !important; font-weight: bold; font-size: 16px; }}
    .stats-bar {{ background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 1px solid #D4AF37; }}
    .stat-item {{ color: #D4AF37; font-weight: bold; font-size: 14px; margin: 0 10px; }}
    .fiche-info {{ background: white; padding: 20px; border-radius: 10px; color: #003366 !important; border: 2px dashed #D4AF37; margin-top: 15px; }}
    .fiche-info h4, .fiche-info p {{ color: #003366 !important; }}
    .chat-message {{ background-color: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px; margin-bottom: 10px; border-left: 4px solid #D4AF37; }}
    [data-testid="stForm"] {{ border: 1px solid #D4AF37 !important; padding: 20px !important; border-radius: 15px; max-width: 400px; margin: auto; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; width: 100%; border-radius: 20px; border: none; height: 3em; }}
    input, .stSelectbox {{ background-color: #f0f2f6 !important; color: black !important; border-radius: 10px !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS TECHNIQUES ---
def make_circle(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        size = (300, 300)
        img = ImageOps.fit(img, size, centering=(0.5, 0.5))
        mask = Image.new('L', size, 0); draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        img.putalpha(mask)
        return img
    except: return None

def verifier_whatsapp_gabon(numero):
    pattern = r"^(074|076|077|062|065|066)\d{6}$"
    return re.match(pattern, numero)

def generer_pdf_officiel(nom, contact, serie, filiere):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "PLATEFORME D'INFORMATION AUX CONCOURS DES GRANDES ÉCOLES PUBLIQUES & PRIVÉES", ln=True, align='C')
    if os.path.exists(LOGO_PATH):
        pdf.image(LOGO_PATH, x=90, y=25, w=30)
        pdf.ln(35)
    else: pdf.ln(15)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "FICHE D'INFORMATION PICGEPP", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, f"Nom complet : {nom.upper()}", ln=True)
    pdf.cell(0, 10, f"Contact WhatsApp : {contact}", ln=True)
    pdf.cell(0, 10, f"Série du BAC : {serie}", ln=True)
    pdf.cell(0, 10, f"Filière visée : {filiere}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "AVANTAGES DU CANDIDAT :", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, "- Droit de participation GRATUITE à un concours blanc de préparation.\n- Remise spéciale sur l'achat du Guide du Bachelier (Anciennes épreuves + Corrections).")
    qr_data = f"PICGEPP GABON | Candidat: {nom} | Tel: {contact}"
    qr = qrcode.make(qr_data)
    qr_path = "temp_qr.png"
    qr.save(qr_path)
    pdf.image(qr_path, x=85, y=pdf.get_y() + 10, w=40)
    return pdf.output(dest='S').encode('latin1')

# --- HEADER (LOGO CENTRÉ ET TITRE) ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_circ = make_circle(LOGO_PATH)
    if logo_circ: st.image(logo_circ, width=120)
    else: st.markdown("<div style='width:100px; height:100px; border-radius:50%; background:#D4AF37; margin:auto; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold; font-size:24px;'>PIC</div>", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)

# --- BANDE DÉROULANTE (ROUGE) ---
st.markdown('<div class="urgent-box"><marquee class="marquee-text">Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous pour rester informés !</marquee></div>', unsafe_allow_html=True)

# --- STATISTIQUES TEMPS RÉEL ---
def obtenir_stats():
    total = len(pd.read_csv(DB_FILE)) if os.path.exists(DB_FILE) else 0
    en_ligne = int(total * random.uniform(0.05, 0.12)) + random.randint(5, 15)
    return total, en_ligne

total, online = obtenir_stats()
st.markdown(f'<div class="stats-bar"><span class="stat-item">👥 Inscrits : {total}</span><span class="stat-item">🟢 En ligne : {online}</span></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL CANDIDAT", "ESPACE ÉTABLISSEMENT", "SUPER ADMINISTRATION"])

# --- 1. ESPACE CANDIDAT ---
if menu == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align: center; font-weight: bold;'>Identifiez-vous pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("Contact WhatsApp (ex: 077123456)")
            serie = st.selectbox("Série du BAC", ["-- Choisir --", "A1", "A2", "B", "C", "D", "E", "F", "G"])
            filiere = st.selectbox("Filière souhaitée", LISTE_FILIERES)
            choix_ecole = st.selectbox("Université privée d'intérêt (Facultatif)", ["Aucun"] + list(ECOLES_PRIVEES.keys()))
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact and verifier_whatsapp_gabon(contact) and filiere != "-- Choisissez une filière --":
                    pd.DataFrame({
                        "Date": [datetime.now().strftime("%d/%m/%Y %H:%M")],
                        "Nom": [nom], "Contact": [contact], "Série": [serie], "Filière": [filiere], "Ecole_Cible": [choix_ecole]
                    }).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
                    st.session_state.auth = True
                    st.session_state.user = {"nom": nom, "contact": contact, "serie": serie, "filiere": filiere}
                    st.rerun()
                else: st.error("Veuillez remplir les champs correctement.")
    else:
        tab1, tab2 = st.tabs(["📄 Ma Fiche PICGEPP", "💬 Forum Discussion"])
        with tab1:
            st.markdown(f"""<div class="fiche-info"><h4 style="text-align:center;">📄 FICHE D'INFORMATION PICGEPP</h4><p><b>Candidat :</b> {st.session_state.user['nom']}<br><b>Série :</b> {st.session_state.user['serie']}<br><b>Contact :</b> {st.session_state.user['contact']}</p><p>✅ <b>Avantages :</b> Concours blanc gratuit + Remise Guide du Bachelier.</p></div>""", unsafe_allow_html=True)
            pdf_bytes = generer_pdf_officiel(st.session_state.user['nom'], st.session_state.user['contact'], st.session_state.user['serie'], st.session_state.user['filiere'])
            st.download_button("📥 Télécharger ma Fiche (PDF)", data=pdf_bytes, file_name=f"Fiche_PICGEPP_{st.session_state.user['nom']}.pdf", mime="application/pdf")
        with tab2:
            st.subheader("💬 Échanges entre Candidats")
            msg = st.text_input("Posez votre question...")
            if st.button("Envoyer ✈️") and msg:
                pd.DataFrame({"Date":[datetime.now().strftime("%H:%M")], "User":[st.session_state.user['nom']], "Message":[msg]}).to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False)
                st.rerun()
            if os.path.exists(CHAT_FILE):
                df_chat = pd.read_csv(CHAT_FILE).iloc[::-1]
                for i, row in df_chat.head(10).iterrows():
                    st.markdown(f'<div class="chat-message"><b>{row["User"]}</b> : {row["Message"]}</div>', unsafe_allow_html=True)
        st.button("Déconnexion", on_click=lambda: st.session_state.update({"auth": False}))

# --- 2. ESPACE ÉTABLISSEMENT ---
elif menu == "ESPACE ÉTABLISSEMENT":
    st.subheader("🔑 Accès Partenaire Établissement")
    ecole = st.selectbox("Sélectionnez votre établissement", list(ECOLES_PRIVEES.keys()))
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if ECOLES_PRIVEES.get(ecole) == pwd: st.session_state.ecole_auth = ecole
        else: st.error("Identifiants incorrects.")
    if 'ecole_auth' in st.session_state:
        st.success(f"Espace réservé à : {st.session_state.ecole_auth}")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            df_filtre = df[df['Ecole_Cible'] == st.session_state.ecole_auth]
            st.dataframe(df_filtre)
            st.download_button("Exporter la liste (Excel)", df_filtre.to_csv(index=False), "candidats.csv")
        st.button("Quitter", on_click=lambda: st.session_state.pop('ecole_auth'))

# --- 3. SUPER ADMINISTRATION ---
elif menu == "SUPER ADMINISTRATION":
    master_pwd = st.text_input("Code de Sécurité Administrateur", type="password")
    if master_pwd == ADMIN_PASSWORD_MASTER:
        st.success("Mode Administrateur activé.")
        if os.path.exists(DB_FILE):
            df_all = pd.read_csv(DB_FILE)
            st.write("### Base de Données Globale")
            st.dataframe(df_all)
            st.write(f"Total des inscrits : {len(df_all)}")
            if st.button("Vider le Forum"):
                if os.path.exists(CHAT_FILE): os.remove(CHAT_FILE); st.rerun()
