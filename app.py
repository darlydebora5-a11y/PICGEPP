import streamlit as st
import pandas as pd
import os
import csv
from datetime import datetime
from PIL import Image, ImageOps, ImageDraw

# --- CONFIGURATION ---
st.set_page_config(page_title="PICGEPP Gabon", layout="wide", page_icon="🇬🇦")

ADMIN_PASSWORD_MASTER = "PICGEPPMPIGA19940421"
DB_FILE = "base_candidats.csv"
LOGO_PLATEFORME = "logo.png"

# Liste des universités privées pour le "Plan B"
PARTENAIRES_PRIVES = ["Aucun", "EM-GABON", "UNIVGA", "IUSTE", "AUI", "BBS", "AUI Business School"]

# --- STYLE CSS LUXE (Bleu Nuit & Doré) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #002b5c; }}
    .header-bar {{ display: flex; align-items: center; border-bottom: 2px solid #D4AF37; padding-bottom: 10px; margin-bottom: 30px; }}
    .main-title-small {{ color: #D4AF37 !important; font-size: 20px !important; font-weight: bold; text-transform: uppercase; margin-left: 15px; }}
    
    /* Formulaire Moderne */
    [data-testid="stForm"] {{ 
        background-color: #003a7d !important;
        border: 2px solid #D4AF37 !important; 
        border-radius: 20px !important; 
        padding: 25px !important;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5) !important;
    }}
    
    h1, h2, h3, h4, p, label, span {{ color: #D4AF37 !important; }}
    
    .stButton>button {{ 
        background: linear-gradient(90deg, #D4AF37 0%, #f7e08a 100%); 
        color: #002b5c !important; 
        font-weight: bold; 
        border-radius: 50px; 
        border: none; 
        transition: 0.3s;
    }}
    
    /* Cartes des Écoles Publics */
    .school-card {{ background: white; padding: 10px; border-radius: 12px; text-align: center; border: 2px solid #D4AF37; margin-bottom: 10px; }}
    .school-name {{ color: #002b5c !important; font-weight: bold; font-size: 13px; }}
    
    input, .stSelectbox {{ background-color: #ffffff !important; color: #002b5c !important; border-radius: 10px !important; }}
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

# --- BARRE DE NAVIGATION ---
st.sidebar.markdown("### ⚙️ NAVIGATION")
espace_pro = st.sidebar.radio("Espace :", ["ACCUEIL CANDIDAT", "ESPACE ÉCOLE PRIVÉE", "ADMINISTRATION"])

# --- HEADER ---
st.markdown('<div class="header-bar">', unsafe_allow_html=True)
col_logo, col_text = st.columns([1, 5])
with col_logo:
    logo = make_small_circle(LOGO_PLATEFORME)
    if logo: st.image(logo, width=70)
with col_text:
    st.markdown('<div class="main-title-small">Plateforme d’Information aux Concours des Grandes Écoles Publiques & Privées au Gabon</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIQUE ---
if espace_pro == "ACCUEIL CANDIDAT":
    if 'auth' not in st.session_state: st.session_state.auth = False
    
    if not st.session_state.auth:
        st.markdown('<div style="background:white; color:red; padding:10px; border-radius:10px; text-align:center; font-weight:bold; margin-bottom:20px;"><marquee>Urgent : Concours des Grandes Écoles Publiques en vue... Inscrivez-vous gratuitement pour rester informés !</marquee></div>', unsafe_allow_html=True)
        
        _, col_f, _ = st.columns([1, 3, 1])
        with col_f:
            with st.form("inscription_gratuite"):
                st.markdown("<h3 style='text-align:center;'>Inscription Gratuite</h3>", unsafe_allow_html=True)
                
                nom_complet = st.text_input("Nom complet")
                whatsapp = st.text_input("Numéro WhatsApp (pour les alertes)")
                
                c1, c2 = st.columns(2)
                with c1:
                    sexe = st.selectbox("Sexe", ["Masculin", "Féminin"])
                    serie = st.selectbox("Série du BAC", ["A1", "A2", "B", "C", "D", "E", "F", "G"])
                with c2:
                    nationalite = st.selectbox("Nationalité", ["Gabonaise", "Étrangère"])
                    filiere = st.text_input("Filière souhaitée (ex: Droit, Médecine)")

                choix_prive = st.selectbox(
                    "🏫 En cas d'échec aux concours publics, quelle école privée souhaitez-vous rejoindre ?",
                    PARTENAIRES_PRIVES
                )
                
                if st.form_submit_button("VALIDER MON INSCRIPTION"):
                    if nom_complet and whatsapp:
                        st.session_state.auth = True
                        st.session_state.u = {"n": nom_complet, "w": whatsapp}
                        # Sauvegarde CSV (Correction ParserError)
                        new_data = pd.DataFrame({
                            "Date": [datetime.now().strftime("%d/%m/%Y %H:%M")],
                            "Nom": [nom_complet], "WhatsApp": [whatsapp], "Sexe": [sexe],
                            "Nationalite": [nationalite], "Serie": [serie], 
                            "Filiere": [filiere], "Choix_Prive": [choix_prive]
                        })
                        new_data.to_csv(DB_FILE, mode='a', header=not os.path.exists(DB_FILE), index=False, quoting=csv.QUOTE_ALL)
                        st.rerun()
    else:
        # Dashboard avec logos réels
        st.markdown(f"### 👋 Ravi de vous voir, {st.session_state.u['n']}")
        c_inf, c_dis = st.columns([3, 1])
        with c_inf:
            st.markdown("#### 🏛️ Actualités des Écoles Publiques")
            ecoles = ["ENS", "ENSET", "IST", "INSG", "ITO", "IUSO", "USS", "USTM", "INSAB"]
            grid = st.columns(3)
            for i, e in enumerate(ecoles):
                with grid[i % 3]:
                    st.markdown(f'<div class="school-card">', unsafe_allow_html=True)
                    img_p = f"{e.lower()}.png"
                    if os.path.exists(img_p): st.image(img_p, width=50)
                    else: st.write(f"🏛️ {e}")
                    st.markdown(f'<div class="school-name">{e}</div></div>', unsafe_allow_html=True)
        with c_dis:
            st.markdown("#### 💬 Chat")
            st.info("Espace de discussion activé.")
            if st.button("Se déconnecter"): st.session_state.auth = False; st.rerun()

elif espace_pro == "ADMINISTRATION":
    if st.text_input("Code Maître", type="password") == ADMIN_PASSWORD_MASTER:
        if os.path.exists(DB_FILE):
            df = pd.read_csv(DB_FILE, on_bad_lines='skip')
            st.dataframe(df)
            st.markdown(f"**Total candidats inscrits : {len(df)}**")
