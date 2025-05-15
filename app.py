import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai



# Configura la pagina
st.set_page_config(page_title="PrompTop", layout="centered")
css_path = os.path.join(os.path.dirname(__file__), "style.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

import base64
from pathlib import Path
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
      img_to_bytes(img_path)
    )
    return img_html
def img_to_base64(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

# Titolo

#footer_logo_path = "loghi png_Tavola disegno 1.png"

#st.markdown(
#    f"""
#    <div style='position: absolute; top: 1rem; left: 1rem; z-index: 10;'>
#        <img src="data:image/png;base64,{img_to_base64(footer_logo_path)}" style="width: 120px;" />
#    </div>
#    """,
#    unsafe_allow_html=True
#)


st.title("PrompTop")
st.markdown(
    "<h4 style='text-align: center;'>Built <span style='color:#38D430;'>for top</span> prompts</h4>",
    unsafe_allow_html=True
)


# Carica API key da .env o secrets
load_dotenv()
genai.configure(api_key=st.secrets["google"]["api_key"])

# Funzione per ottenere i modelli disponibili
#@st.cache_data
#def get_text_models():
#    models = genai.list_models()
#    return [m.name for m in models if "generateContent" in m.supported_generation_methods]'''



#st.sidebar.markdown(
#    f"<div style='text-align: center;'>{img_to_html(footer_logo_path)}</div>",
#    unsafe_allow_html=True
#)


#st.sidebar.title("⚙️ Configurazione")
#available_models = get_text_models()
#selected_model = st.sidebar.selectbox("Seleziona modello Gemini", options=available_models)
model = genai.GenerativeModel(model_name="gemini-2.0-flash-001")


# Funzione per ripulire il testo
def clean_response(text: str) -> str:
    lines = text.strip().splitlines()
    return "\n".join(line for line in lines if not line.strip().startswith("```")).strip()

# Agenti
def refine_prompt(prompt):
    system = (
        "Sei un esperto nella scrittura di prompt per LLM. "
        "Riformula il seguente testo in un prompt ottimale: preciso, efficiente, ben strutturato, "
        "mantenendo l'intento originale e senza cambiare il significato."
    )
    response = model.generate_content([system, prompt])
    return response.text.strip()

def critique_prompt(prompt):
    critic_prompt = (
        "Agisci come un critico esperto di prompt per LLM. Analizza il prompt seguente "
        "e indica eventuali ambiguità, mancanze, ridondanze o suggerimenti di miglioramento:\n\n"
        f"Prompt: {prompt}"
    )
    response = model.generate_content(critic_prompt)
    return response.text.strip()

def rewrite_prompt_with_feedback(prompt, feedback):
    rewrite_prompt = (
        f"Prendi questo prompt:\n{prompt}\n\n"
        f"E riformulalo tenendo conto delle seguenti osservazioni:\n{feedback}\n\n"
        "Riscrivi il prompt ottimizzato. Restituisci solo il testo del prompt, senza spiegazioni o commenti."
        "Inserisci anche le seguenti istruzioni:"
        "Fornisci una risposta sintetica e diretta, senza ripetizioni né frasi introduttive generiche."
        "Evita spiegazioni ovvie o banali che presuppongono conoscenze di base già note."
        "Non aggiungere dettagli superflui o informazioni non richieste."
        "Rimani strettamente aderente alla domanda posta, senza andare fuori tema."
        "Usa uno stile conciso, tecnico e focalizzato sui concetti chiave richiesti."
        "Evita generalizzazioni e fornisci solo informazioni specifiche e rilevanti."
        "Non includere disclaimer, avvertenze o frasi di circostanza."
        "Presenta la risposta in elenco puntato o numerato se aiuta la chiarezza."
        "Non semplificare eccessivamente i concetti: punta a un livello medio-alto di precisione tecnica."
        "Evita espressioni vaghe come 'potrebbe essere', 'in alcuni casi', a meno che non siano strettamente necessarie per correttezza concettuale."
    )
    response = model.generate_content(rewrite_prompt)
    return response.text.strip()

# UI principale
user_input = st.text_area("✍️ Inserisci il prompt da migliorare", height=200)

if st.button("🚀 Raffina e Analizza"):
    if not user_input.strip():
        st.warning("⚠️ Inserisci prima un prompt.")
    else:
        with st.spinner("🛠️ Agente Refiner al lavoro..."):
            refined = refine_prompt(user_input)
        st.subheader("🎯 Prompt Raffinato")
        st.code(refined)

        with st.spinner("🔍 Agente Critic in azione..."):
            critique = critique_prompt(refined)
        st.subheader("🧠 Analisi del Critico")
        st.write(critique)

        with st.spinner("✍️ Agente Rewriter sta sistemando il prompt..."):
            final_prompt = rewrite_prompt_with_feedback(refined, critique)
        st.subheader("✅ Prompt Finalizzato")
        st.code(final_prompt)

        st.download_button(
            label="📥 Scarica Prompt Finalizzato",
            data=final_prompt,
            file_name="prompt_finalizzato.txt",
            mime="text/plain"
        )
        st.success("🎉 Pipeline completata con successo!")
