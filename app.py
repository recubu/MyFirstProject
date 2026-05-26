import streamlit as st
import json
import requests
from google import genai
from google.genai import types

# 1. Configuración visual con los colores corporativos de TProtege
st.set_page_config(page_title="Generador de Contenidos TProtege", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .stButton>button {
        background-color: #4d8d8f;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #8bb53e;
        color: white;
    }
    h1, h2, h3 {
        color: #4d8d8f;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Sistema de Contenidos - TProtege")
st.subheader("Ingeniería Audiovisual e Integración Tecnológica")

# 2. Configuración en la barra lateral (Leyendo de los Secrets guardados)
st.sidebar.header("Configuración de Conexión")
api_key = st.sidebar.text_input("Introduce tu Gemini API Key:", value=st.secrets.get("GEMINI_API_KEY", ""), type="password")
webhook_url = st.sidebar.text_input("URL Webhook de Make:", value=st.secrets.get("MAKE_WEBHOOK_URL", ""), placeholder="https://hook.eu1.make.com/...")

# 3. Formulario de entrada
st.markdown("### 📝 Configuración de la Pieza de Contenido")
col1, col2 = st.columns(2)

with col1:
    red_social = st.selectbox("Red Social", ["LinkedIn", "Instagram", "TikTok", "Facebook"])
    publico = st.text_input("Público Objetivo", placeholder="Ej: Decanos, Directores de TI...")
    objetivo = st.text_input("Objetivo de la publicación", placeholder="Ej: Autoridad, Generar Leads...")

with col2:
    tema = st.text_input("Tema / Tecnología de TProtege", placeholder="Ej: Cabinas holográficas...")
    cta = st.text_input("Llamada a la acción (CTA)", placeholder="Ej: Visita nuestra web...")
    restricciones = st.text_input("Restricciones (Opcional)", placeholder="Ej: Sin tecnicismos...")

system_instruction = """
Eres el Cerebro Orquestador de la App de Contenidos de TProtege (tprotege.es), empresa líder en Ingeniería Audiovisual e Integración Tecnológica. Tu rol combina: Arquitecta full-stack, diseñadora UX, ingeniera de prompts y experta en automatizaciones con Make. Actúas bajo un flujo de 3 pasos: Configurar -> Generar -> Enviar a Webhook.

MÉTODO DE INTERACCIÓN:
Devuelve un objeto JSON puro y directo que contenga exactamente la siguiente estructura. No agregues texto antes ni después del JSON, responde SOLO con el objeto JSON para que el sistema lo pueda procesar:
{
  "ideas_estrategicas": ["Lista de las 10 ideas cortas generadas"],
  "idea_seleccionada": "Nombre de la idea elegida proactivamente",
  "platform": "Red social",
  "format": "Formato visual idóneo",
  "objective": "Objetivo fijado",
  "caption": "El copy final redactado en masculino neutro B2B, usando frases cortas, espacios y saltos de línea",
  "hashtags": ["lista", "de", "hashtags"],
  "image_prompt": "Sugerencia de diseño o enfoque visual para la publicación (orientación vertical)",
  "metadata": { "target_audience": "Público objetivo", "cta_link": "Link correspondiente" }
}
"""

if st.button("✨ Generar Pack de Contenido"):
    if not api_key:
        st.error("❌ Por favor, introduce tu Gemini API Key en la barra lateral.")
    else:
        with st.spinner("🤖 El motor de TProtege está designing tu contenido..."):
            try:
                client = genai.Client(api_key=api_key)
                user_prompt = f"Genera el contenido con estos datos: Red: {red_social}, Público: {publico}, Objetivo: {objetivo}, Tema: {tema}, CTA: {cta}, Restricciones: {restricciones}"
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        response_mime_type="application/json"
                    )
                )
                
                # Guardar el resultado en la sesión de la App
                st.session_state['json_data'] = json.loads(response.text)
                st.success("🎉 ¡Contenido estructurado con éxito!")
                
            except Exception as e:
                st.error(f"Hubo un error al generar: {e}")

# Si hay datos generados, los mostramos ordenados y habilitamos el envío
if 'json_data' in st.session_state:
    data = st.session_state['json_data']
    
    st.markdown("---")
    st.subheader("📋 Contenido Propuesto para Publicación")
    
    st.markdown(f"**Idea Ganadora:** {data.get('idea_seleccionada')}")
    st.text_area("✍️ Copy Redactado (Masculino Neutro B2B):", value=data.get('caption'), height=250)
    st.text_input("🖼️ Enfoque Visual Sugerido:", value=data.get('image_prompt'))
    
    st.markdown("### 🔄 Conexión con Ecosistema de Automatización")
    if st.button("📤 Enviar Pack Listo a Make"):
        if not webhook_url:
            st.error("❌ Falta la URL del Webhook de Make en la barra lateral.")
        else:
            with st.spinner("Enviando datos..."):
                try:
                    res = requests.post(webhook_url, json=data)
                    if res.status_code == 200:
                        st.success("🚀 ¡Datos guardados en tu Google Sheets correctamente!")
                    else:
                        st.error(f"Make recibió los datos pero respondió con error: {res.status_code}")
                except Exception as e:
                    st.error(f"Error en la conexión de red: {e}")
