import streamlit as st
import os
import google.generativeai as genai
from fpdf import FPDF
import re
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="DELE Tutor AI", page_icon="🎓")

# --- SISTEMA DE TRADUCCIÓN (DICCIONARIO) ---
TRANSLATIONS = {
    "Español": {
        "sidebar_title": "Configuración",
        "lang_select": "Idioma de la Interfaz",
        "level_select": "Selecciona tu Nivel",
        "topic_select": "Selecciona un Tema",
        "start_btn": "Comenzar Conversación",
        "reset_btn": "Reiniciar Sesión",
        "chat_col": "Chat con Tutor IA",
        "notes_col": "Pizarra Gramatical",
        "placeholder": "Escribe tu mensaje en español...",
        "download_pdf": "Descargar Informe (PDF)",
        "contact_btn": "Contactar Profesor Nativo",
        "diag_mode": "Modo Diagnóstico (Automático)",
        "select_prompt": "Selecciona...",
        "api_error": "Por favor configura tu API Key en los secretos de Streamlit."
    },
    "English": {
        "sidebar_title": "Settings",
        "lang_select": "Interface Language",
        "level_select": "Select Level",
        "topic_select": "Select Topic",
        "start_btn": "Start Conversation",
        "reset_btn": "Reset Session",
        "chat_col": "AI Tutor Chat",
        "notes_col": "Grammar Board",
        "placeholder": "Type your message in Spanish...",
        "download_pdf": "Download Report (PDF)",
        "contact_btn": "Contact Native Teacher",
        "diag_mode": "Diagnostic Mode (Auto)",
        "select_prompt": "Select...",
        "api_error": "Please configure your API Key in Streamlit secrets."
    },
    "中文 (繁體)": {
        "sidebar_title": "設定",
        "lang_select": "介面語言",
        "level_select": "選擇等級",
        "topic_select": "選擇主題",
        "start_btn": "開始對話",
        "reset_btn": "重置會話",
        "chat_col": "AI 導師聊天",
        "notes_col": "文法白板",
        "placeholder": "用西班牙語輸入您的訊息...",
        "download_pdf": "下載報告 (PDF)",
        "contact_btn": "聯繫母語老師",
        "diag_mode": "診斷模式 (自動)",
        "select_prompt": "選擇...",
        "api_error": "請在 Streamlit secrets 中配置您的 API Key。"
    }
}

# --- FUNCIONES AUXILIARES ---

def get_prompts_structure():
    """Escanea la carpeta 'prompts' y devuelve una estructura de dict."""
    prompts_path = "prompts"
    structure = {}
    if not os.path.exists(prompts_path):
        os.makedirs(prompts_path) # Crear si no existe para evitar error
        return structure
    
    # Listar carpetas de nivel (ordenadas)
    levels = sorted([d for d in os.listdir(prompts_path) if os.path.isdir(os.path.join(prompts_path, d)) and d != "System"])
    
    for level in levels:
        # Limpiar nombre para visualización (ej: "01_Nivel_A1" -> "Nivel A1")
        display_name = level.replace("_", " ").split(" ", 1)[1] if "_" in level else level
        
        files = sorted([f for f in os.listdir(os.path.join(prompts_path, level)) if f.endswith(".txt")])
        topics = {f.replace(".txt", "").replace("_", " "): os.path.join(prompts_path, level, f) for f in files}
        
        structure[display_name] = topics
    return structure

def load_prompt_content(filepath):
    """Lee el contenido de un archivo de texto."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: Archivo no encontrado."

def parse_response(text):
    """
    Separa el texto normal de las notas gramaticales envueltas en <nota>...</nota>.
    Devuelve: (texto_chat_limpio, lista_de_notas)
    """
    pattern = r"<nota>(.*?)</nota>"
    notes = re.findall(pattern, text, re.DOTALL)
    clean_text = re.sub(pattern, "", text, flags=re.DOTALL).strip()
    return clean_text, notes

def create_pdf(history, notes_history):
    """Genera un PDF simple con el historial."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Informe de Sesión - DELE Tutor AI", ln=1, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10)
    for role, text in history:
        clean_text, _ = parse_response(text) if role == "model" else (text, [])
        # Nota: FPDF básico tiene problemas con caracteres chinos/tildes complejos. 
        # En producción se recomienda usar librerías con soporte UTF-8 completo como fpdf2 + fuentes TTF.
        # Aquí usamos encode/decode 'latin-1' para simplificar el ejemplo en español básico.
        safe_text = f"{role.upper()}: {clean_text}"
        try:
            pdf.multi_cell(0, 10, safe_text.encode('latin-1', 'replace').decode('latin-1'))
        except:
            pdf.multi_cell(0, 10, f"{role.upper()}: [Contenido con caracteres no soportados en PDF básico]")
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1')

# --- INICIO DE LA APP ---

# 1. Selector de Idioma (Sidebar)
with st.sidebar:
    lang_option = st.selectbox("Language / Idioma", ["Español", "English", "中文 (繁體)"])
    T = TRANSLATIONS[lang_option] # Cargar textos traducidos
    st.title(T["sidebar_title"])

    # 2. Configuración API (Desde Secrets o Input)
    # Intenta leer de secrets, si no, pide input (útil para desarrollo)
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        api_key = st.text_input("Google API Key", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
    else:
        st.error(T["api_error"])
        st.stop()

    # 3. Menús Dinámicos
    prompts_data = get_prompts_structure()
    
    selected_level_name = st.selectbox(T["level_select"], [T["select_prompt"]] + list(prompts_data.keys()))
    
    selected_prompt_path = None
    system_prompt_content = ""

    if selected_level_name != T["select_prompt"]:
        # Si eligió nivel, mostrar temas
        topics_dict = prompts_data[selected_level_name]
        selected_topic_name = st.selectbox(T["topic_select"], list(topics_dict.keys()))
        selected_prompt_path = topics_dict[selected_topic_name]
    else:
        # MODO DIAGNÓSTICO (Por defecto)
        st.info(T["diag_mode"])
        selected_prompt_path = "prompts/System/Diagnostic_Mode.txt"

    # Botón de Reinicio/Carga
    if st.button(T["reset_btn"], use_container_width=True):
        st.session_state.history = []
        st.session_state.notes_history = []
        st.session_state.current_prompt = ""
        st.rerun()

# --- LÓGICA DEL CHAT ---

# Inicializar estado
if "history" not in st.session_state:
    st.session_state.history = []
if "notes_history" not in st.session_state:
    st.session_state.notes_history = [] # Para guardar notas gramaticales acumuladas

# Cargar el prompt seleccionado si cambió
try:
    if selected_prompt_path:
        raw_prompt = load_prompt_content(selected_prompt_path)
        # INYECCIÓN TÉCNICA: Instruir a la IA sobre el formato XML para la columna derecha
        technical_instruction = """
        [INSTRUCCIÓN DEL SISTEMA]: Eres un tutor en una app de pantalla dividida.
        IMPORTANTE: Si das una explicación gramatical, corrección o vocabulario clave, DEBES envolverlo en etiquetas <nota>...</nota>.
        Ejemplo: "Muy bien. <nota>Recuerda que 'casa' es femenino.</nota> ¿Seguimos?"
        El texto dentro de <nota> se mostrará en una pizarra separada. El resto va al chat.
        """
        st.session_state.system_prompt = raw_prompt + "\n" + technical_instruction
except Exception as e:
    st.error(f"Error cargando prompt: {e}")

# Layout Principal
col_chat, col_notes = st.columns([0.7, 0.3])

with col_chat:
    st.subheader(T["chat_col"])
    
    # Mostrar historial
    for role, text in st.session_state.history:
        clean_text, _ = parse_response(text) if role == "model" else (text, [])
        with st.chat_message(role):
            st.markdown(clean_text)

    # Input del usuario
    if prompt := st.chat_input(T["placeholder"]):
        # 1. Mostrar usuario
        st.chat_message("user").markdown(prompt)
        st.session_state.history.append(("user", prompt))

        # 2. Llamar a Gemini
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite') # Modelo 2025
            
            # Construir contexto (System Prompt + Historial reciente)
            chat = model.start_chat(history=[
                {"role": "user", "parts": [st.session_state.system_prompt]},
                {"role": "model", "parts": ["Entendido. Configuración cargada. Estoy listo para actuar según el prompt."]}
            ])
            
            # Enviar historial previo (simplificado para este ejemplo)
            # En producción, gestionar el tamaño del contexto.
            for role, msg in st.session_state.history[:-1]: 
                # Mapear roles de streamlit a gemini
                g_role = "user" if role == "user" else "model"
                chat.history.append({"role": g_role, "parts": [msg]})

            response = chat.send_message(prompt)
            full_response = response.text
            
            # 3. Procesar respuesta (Separar XML)
            clean_text, new_notes = parse_response(full_response)
            
            # Guardar en estado
            st.session_state.history.append(("model", full_response))
            if new_notes:
                st.session_state.notes_history.extend(new_notes)
            
            # Mostrar respuesta IA
            with st.chat_message("model"):
                st.markdown(clean_text)
                
            st.rerun() # Recargar para actualizar la columna de notas
            
        except Exception as e:
            st.error(f"Error de API: {e}")

with col_notes:
    st.subheader(T["notes_col"])
    st.markdown("---")
    if st.session_state.notes_history:
        for i, note in enumerate(reversed(st.session_state.notes_history)): # Mostrar las más nuevas arriba
            st.info(note)
    else:
        st.caption("Las notas gramaticales aparecerán aquí.")

# --- FOOTER (PDF y Contacto) ---
st.divider()
col_pdf, col_contact = st.columns(2)

with col_pdf:
    if st.session_state.history:
        pdf_bytes = create_pdf(st.session_state.history, st.session_state.notes_history)
        st.download_button(
            label=T["download_pdf"],
            data=bytes(pdf_bytes),
            file_name="informe_clase_dele.pdf",
            mime="application/pdf",
        )

with col_contact:
    contact_url = "https://docs.google.com/forms/d/e/1FAIpQLSe0CbV2SvDRh7YR68IjdW-E7D0TkqomaLwYk_GvTmJIw5eLlQ/viewform?usp=header"
    st.link_button(T["contact_btn"], contact_url, type="primary")
