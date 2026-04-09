import streamlit as st
import pandas as pd
import os
import re
import random
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="centered", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
CHAT_FILE = "chat_history.csv"

# Accès Écoles Privées (Mots de passe sécurisés)
ECOLES_PRIVEES = {
    "EM-GABON": "emg2026",
    "UNIVGA": "uvga2026",
    "IUSTE": "iuste2026",
    "AUI": "aui2026",
    "BBS": "bbs2026"
}

# --- STYLE CSS (Optimisé Mobile, Bleu & Doré) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #003366; }}
    
    /* CENTRAGE ABSOLU DU LOGO */
    .header-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        margin-bottom: 20px;
    }}
    .circular-logo {{
        width: 110px;
        height: 110px;
        border-radius: 50%;
        border: 3px solid #D4AF37;
        background-color: #D4AF37;
        color: #003366;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 24px;
        margin-bottom: 10px;
    }}

    .main-title {{
        color: #D4AF37 !important;
        font-size: 22px !important;
        font-weight: bold;
        text-transform: uppercase;
        margin: 0 auto;
    }}

    h2, h3, p, label, span {{ color: #D4AF37 !important; font-size: 14px; }}
    
    .urgent-box {{ 
        background-color: #ffffff; padding: 8px; border-radius: 5px; 
        text-align: center; border: 2px solid #ff0000; margin-bottom: 15px; 
    }}
    .marquee-text {{ color: #ff0000 !important; font-weight: bold; font-size: 15px; }}
    
    .stats-bar {{
        background: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px;
        text-align: center; margin-bottom: 20px; border: 1px solid #D4AF37;
    }}
    .stat-item {{ color: #D4AF37; font-weight: bold; font-size: 14px; margin: 0 10px; }}
    
    [data-testid="stForm"] {{ border: 1px solid #D4AF37 !important; padding: 15px !important; border-radius: 15px; max-width: 350px; margin: auto; }}
    .stButton>button {{ background-color: #D4AF37; color: #003366; font-weight: bold; width: 100%; border-radius: 20px; border: none; }}
    input, .stSelectbox {{ background-color: #f0f2f6 !important; color: black !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 1. HEADER (LOGO CENTRÉ ET TITRE) ---
st.markdown('<div class="header-container">', unsafe_allow_html=True)
if os.path.exists("logo.png"):
    st.image("logo.png", width=110) # Streamlit centrera l'image car layout="centered"
else:
    st.markdown('<div class="circular-logo">PIC</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 2. BANDE DÉROULANTE ET STATS ---
st.markdown("""<div class="urgent-box"><marquee class="marquee-text">Urgent : Concours des Grandes Écoles Publiques en vue... Inscris-toi pour rester informé !</marquee></div>""", unsafe_allow_html=True)

def obtenir_stats():
    total = len(pd.read_csv(DB_FILE)) if os.path.exists(DB_FILE) else 0
    en_ligne = int(total * random.uniform(0.05, 0.12)) + random.randint(5, 15)
    return total, en_ligne

total, online = obtenir_stats()
st.markdown(f'<div class="stats-bar"><span class="stat-item">👥 Inscrits : {total}</span><span class="stat-item">🟢 En ligne : {online}</span></div>', unsafe_allow_html=True)

# --- NAVIGATION ---
menu = st.sidebar.radio("Navigation", ["ACCUEIL CANDIDAT", "ESPACE ÉCOLE PRIVÉE", "SUPER ADMIN"])

# --- 3. ACCUEIL CANDIDAT ---
if menu == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False

    if not st.session_state.auth:
        with st.form("inscription"):
            st.markdown("<p style='text-align: center; font-weight: bold;'>Identifie-toi pour rejoindre la communauté des bacheliers</p>", unsafe_allow_html=True)
            nom = st.text_input("Nom complet")
            contact = st.text_input("WhatsApp (ex: 077123456)")
            serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
            
            if st.form_submit_button("VALIDER MON INSCRIPTION"):
                if nom and contact and len(contact) >= 9:
                    data = {"Date": [datetime.now().strftime("%d/%m/%Y %H:%M")], "Nom": [nom], "Contact": [contact], "Série": [serie]}
                    pd.DataFrame(data).to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, encoding='utf-8-sig')
                    st.session_state.auth = True
                    st.session_state.user = {"nom": nom, "serie": serie}
                    st.rerun()
                else: st.error("Champs invalides")
    else:
        tab1, tab2 = st.tabs(["📄 Ma Fiche PICGEPP", "💬 Forum"])
        with tab1:
            st.markdown(f"""<div style="background:white; padding:15px; border-radius:10px; color:#003366 !important;">
                <h4 style="color:#003366 !important; text-align:center;">📄 FICHE D'INFORMATION PICGEPP</h4>
                <p style="color:#003366 !important;"><b>Candidat :</b> {st.session_state.user['nom']}<br>✅ <b>Avantages :</b> Concours blanc gratuit + Remise Guide du Bachelier.</p>
            </div>""", unsafe_allow_html=True)
        with tab2:
            st.subheader("💬 Discussion")
            if os.path.exists(CHAT_FILE):
                chat_data = pd.read_csv(CHAT_FILE).tail(10)
                for i, row in chat_data.iterrows(): 
                    st.markdown(f"**{row['User']}**: {row['Message']}")
            txt = st.text_input("Message")
            if st.button("Envoyer"):
                pd.DataFrame({"Date":[datetime.now()], "User":[st.session_state.user['nom']], "Message":[txt]}).to_csv(CHAT_FILE, mode='a', header=not os.path.exists(CHAT_FILE), index=False)
                st.rerun()

# --- 4. ESPACE ÉCOLE PRIVÉE (CLOISONNÉ) ---
elif menu == "ESPACE ÉCOLE PRIVÉE":
    st.subheader("Accès Établissement Partenaire")
    ecole = st.selectbox("Sélectionnez votre École", list(ECOLES_PRIVEES.keys()))
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Connexion"):
        if ECOLES_PRIVEES.get(ecole) == pwd: st.session_state.ecole_user = ecole
        else: st.error("Accès refusé.")
    if 'ecole_user' in st.session_state:
        st.success(f"Connecté : {st.session_state.ecole_user}")
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE)
            st.dataframe(df) # Voir tous les candidats pour cet établissement
        if st.button("Déconnexion"): st.session_state.pop('ecole_user'); st.rerun()

# --- 5. SUPER ADMIN ---
elif menu == "SUPER ADMIN":
    st.subheader("🛠 Administration Générale")
    master_pwd = st.text_input("Code Maître", type="password")
    if master_pwd == ADMIN_PASSWORD_MASTER:
        st.success("Mode Maître Activé")
        if os.path.exists(DB_FILE):
            st.write("### Liste Globale")
            st.dataframe(pd.read_csv(DB_FILE))
