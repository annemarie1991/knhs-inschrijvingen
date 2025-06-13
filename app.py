import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

st.set_page_config(page_title="KNHS Inschrijvingen", layout="wide")
st.title("📅 KNHS Wedstrijdbeheer")

def bestandspad(wedstrijd_bestandsnaam):
    return os.path.join(DATA_DIR, wedstrijd_bestandsnaam + ".json")

def laad_wedstrijd_data(bestandsnaam):
    path = bestandspad(bestandsnaam)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"datum": "", "deelnemers": [], "laatste_upload": None}

def sla_wedstrijd_data_op(bestandsnaam, data):
    with open(bestandspad(bestandsnaam), "w") as f:
        json.dump(data, f, indent=2)

def extract_deelnemers_from_csv(upload):
    df = pd.read_csv(upload, sep=";")
    deelnemers = []
    for _, row in df.iterrows():
        naam = row.get("Naam", "")
        paard = row.get("Sportnaam 1", "")
        klasse = row.get("Klasse", "")
        categorie = row.get("Pony categorie", "")
        opmerkingen = row.get("Opmerkingen", "")
        telefoon = row.get("Mobiele telefoon 0", "")

        if pd.isna(naam) or pd.isna(paard):
            continue

        voornaam = naam.strip().split()[0]
        deelnemer = {
            "naam": naam.strip(),
            "voornaam": voornaam,
            "paard": paard.strip(),
            "klasse": klasse.strip(),
            "categorie": categorie.strip(),
            "telefoon": telefoon.strip(),
            "opmerkingen": opmerkingen.strip() if isinstance(opmerkingen, str) else "",
            "bericht_verzonden": False,
            "notitie": ""
        }
        deelnemers.append(deelnemer)
    return deelnemers

def merge_deelnemers(bestaande, nieuwe):
    bestaand_keys = {(d['naam'], d['paard']) for d in bestaande}
    for d in nieuwe:
        key = (d['naam'], d['paard'])
        if key not in bestaand_keys:
            bestaande.append(d)
    return bestaande

# === Sidebar: wedstrijden beheren ===
with st.sidebar:
    st.header("➕ Nieuwe Wedstrijd")
    naam = st.text_input("Naam wedstrijd")
    datum = st.date_input("Datum")
    if st.button("Toevoegen"):
        file_id = f"{naam}_{datum}".replace(" ", "_")
        path = bestandspad(file_id)
        if not os.path.exists(path):
            sla_wedstrijd_data_op(file_id, {
                "datum": str(datum),
                "deelnemers": [],
                "laatste_upload": None
            })
        st.session_state["wedstrijd"] = file_id
        st.experimental_rerun()

# === Overzicht bestaande wedstrijden ===
wedstrijden = [f.replace(".json", "") for f in os.listdir(DATA_DIR) if f.endswith(".json")]

if wedstrijden:
    st.subheader("📂 Kies een wedstrijd")
    for w in wedstrijden:
        col1, col2 = st.columns([8, 1])
        with col1:
            if st.button(w, key="open_" + w):
                st.session_state["wedstrijd"] = w
                st.experimental_rerun()
        with col2:
            if st.button("🗑️", key="delete_" + w):
                os.remove(bestandspad(w))
                if st.session_state.get("wedstrijd") == w:
                    del st.session_state["wedstrijd"]
                st.experimental_rerun()
else:
    st.info("Nog geen wedstrijden toegevoegd.")

# === Wedstrijddetails en deelnemerslijst ===
wedstrijd = st.session_state.get("wedstrijd")
if wedstrijd:
    data = laad_wedstrijd_data(wedstrijd)
    st.markdown(f"## 📋 Wedstrijd: `{wedstrijd}` — Datum: **{data['datum']}**")
    st.markdown(f"Laatste CSV-upload: `{data['laatste_upload']}`" if data['laatste_upload'] else "_Nog geen upload gedaan_")

    upload = st.file_uploader("📄 Upload CSV-bestand", type="csv")
    if upload:
        nieuwe_deelnemers = extract_deelnemers_from_csv(upload)
        data['deelnemers'] = merge_deelnemers(data['deelnemers'], nieuwe_deelnemers)
        data['laatste_upload'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        sla_wedstrijd_data_op(wedstrijd, data)
        st.success("✅ CSV verwerkt!")

    st.markdown("---")
    st.markdown("### 🧍 Deelnemers")
    for i, d in enumerate(data['deelnemers']):
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 2])
        col1.markdown(f"**{d['naam']}**  \nPaard: *{d['paard']}*")
        col2.markdown(f"📞 {d['telefoon'] or 'Geen nummer'}")
        col3.markdown(f"🏷️ Klasse: {d['klasse']}  \n🐴 Cat: {d['categorie']}")
        col4.markdown(f"🗒️ {d['opmerkingen'] or '_Geen opmerking_'}")
        met_hover = f"Hoi {d['voornaam']}, ik ga beginnen aan de startlijst van {data['datum']}. Laat je weten vanaf hoe laat je kunt starten? We starten het liefst zo vroeg mogelijk."
        col5.checkbox("✅ Bericht gestuurd", value=d["bericht_verzonden"], key=f"vink_{i}", on_change=lambda i=i: data['deelnemers'].__setitem__(i, {**data['deelnemers'][i], "bericht_verzonden": True}))
        notitie = st.text_input("🖊️ Notitie", value=d["notitie"], key=f"note_{i}")
        data['deelnemers'][i]["notitie"] = notitie
        st.markdown(f"<small><i>{met_hover}</i></small>", unsafe_allow_html=True)
        st.markdown("---")

    sla_wedstrijd_data_op(wedstrijd, data)
