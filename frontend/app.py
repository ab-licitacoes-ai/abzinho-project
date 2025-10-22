import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import datetime

# --- IMPORTAÇÃO DOS MÓDULOS ---
# Usando importações relativas, assumindo que estão na mesma pasta 'frontend'
from frontend.config import PAGE_CONFIG, CSS_INJECTIONS
from frontend.data_manager import initialize_session_state
from frontend.ui_components import render_login, render_cadastro, render_sidebar, render_dashboard_content

# --- 1. Configurações Iniciais ---
st.set_page_config(**PAGE_CONFIG)
st.markdown(CSS_INJECTIONS, unsafe_allow_html=True)
initialize_session_state()

# ====================================================
# LOOP PRINCIPAL DA APLICAÇÃO (Routing)
# ====================================================

if st.session_state['logged_in']:
    # --- Página do Dashboard (Conteúdo Principal) ---
    render_sidebar()
    render_dashboard_content()
else:
    # --- Páginas de Autenticação ---
    if st.session_state['page'] == 'login':
        render_login()
    elif st.session_state['page'] == 'cadastro':
        render_cadastro()
