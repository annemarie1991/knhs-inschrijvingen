import streamlit as st
import os
import json
from datetime import datetime

# Map voor wedstrijddata
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="Wedstrijdbeheer", layout="wide")
st.title("📅 Wedstrijdbeheer App")

# Laad bestaande wedstrijden
def load_wedstrijden():
    return [f.replace(".json", "") for f in os.listdir(DATA_DIR) if f.endswith(".json")]

# Voeg nieuwe wedstrijd toe
def save_wedstrijd(wedstrijdnaam, datum):
    filename = f"{wedstrijdnaam}_{datum}.json".replace(" ", "_")
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        with open(filepath, "w") as f:
            json.dump({"datum": datum, "deelnemers": [], "laatste_upload": None}, f)

# Hoofdscherm
with st.sidebar:
    st.header("➕ Nieuwe Wedstrijd Toevoegen")
    naam = st.text_input("Naam wedstrijd")
    datum = st.date_input("Datum")
    if st.button("Wedstrijd toevoegen"):
        save_wedstrijd(naam, datum.strftime("%Y-%m-%d"))
        st.experimental_rerun()

st.subheader("📋 Jouw wedstrijden")

wedstrijden = load_wedstrijden()
if wedstrijden:
    for w in wedstrijden:
        col1, col2 = st.columns([8, 1])
        with col1:
            if st.button(f"📂 Open {w}", key=w):
                st.session_state["selected_wedstrijd"] = w
                st.experimental_rerun()
        with col2:
            if st.button("🗑️", key=f"del_{w}"):
                os.remove(os.path.join(DATA_DIR, w + ".json"))
                st.experimental_rerun()
else:
    st.info("Nog geen wedstrijden toegevoegd.")

# Open een wedstrijd als er één is gekozen
if "selected_wedstrijd" in st.session_state:
    st.subheader(f"📂 Wedstrijd: {st.session_state['selected_wedstrijd']}")
    # Later vullen we deze pagina verder aan
