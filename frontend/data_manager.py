import pandas as pd
import streamlit as st
import requests
from datetime import datetime
from .config import API_BASE_URL, TEAM_MEMBERS, STATUS_TAREFAS, STATUS_CONTATOS, STATUS_ATAS, STATUS_VENDAS

# Complementary functions for data management in Streamlit

def format_currency(value):
    """Formata valor float para a string monetária brasileira R$ X.XXX,XX."""
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def clean_currency(value):
    """Limpa a string monetária para float (para number_input)."""
    if isinstance(value, str) and value.startswith("R$"):
        return float(value.replace('R$', '').replace('.', '').replace(',', '.').strip())
    return value

def initialize_session_state():
    """Inicializa o estado da sessão do Streamlit."""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'active_module' not in st.session_state:
        st.session_state['active_module'] = 'Tarefas'
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    if 'auth_token' not in st.session_state:
        st.session_state['auth_token'] = None
    if 'current_user' not in st.session_state:
        st.session_state['current_user'] = None
    if 'data_cache' not in st.session_state:
        st.session_state['data_cache'] = {}

# Comunication functions with the API

def get_api_headers():
    """Retorna cabeçalhos com o token JWT."""
    token = st.session_state.get('auth_token')
    if token:
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return {"Content-Type": "application/json"}

def get_endpoint(module_name):
    """Mapeia o nome do módulo para o endpoint da API."""
    return {'Tarefas': 'tasks', 'Contatos': 'contacts', 'Atas': 'minutes', 'Vendas': 'sales'}.get(module_name, module_name.lower())


def fetch_data_from_api(module_name):
    """Busca dados do módulo da API e armazena em cache."""
    if module_name in st.session_state['data_cache']:
        return st.session_state['data_cache'][module_name]

    endpoint = get_endpoint(module_name)
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        response = requests.get(url, headers=get_api_headers())
        response.raise_for_status() 
        raw_data = response.json()
        df = pd.DataFrame(raw_data)

        # Rename column database (snake_case) for front-end (Title Case)
        if module_name == 'Tarefas':
            df = df.rename(columns={'task_id': 'ID', 'descricao': 'Descrição', 'data_limite': 'Data Limite', 'data_criacao': 'Data Criação'})
        # Data conversion for date fields
        for col in df.columns:
            if 'data' in col.lower() and df[col].dtype == 'object':
                 try:
                    df[col] = pd.to_datetime(df[col]).dt.date
                 except ValueError:
                    pass
        
        st.session_state['data_cache'][module_name] = df
        return df
        
    except requests.exceptions.ConnectionError:
        st.error("Erro de Conexão: O Back-end da API não está rodando ou está inacessível.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        error_detail = response.json().get('detail', str(e)) if 'response' in locals() and response.content else str(e)
        st.error(f"Erro na API (Status {response.status_code if 'response' in locals() else 'N/A'}): {error_detail}")
        return pd.DataFrame()


def handle_save_api(data, is_editing, item_id):
    """Lógica para salvar e atualizar via API."""
    module = st.session_state['active_module']
    endpoint = get_endpoint(module)
    url = f"{API_BASE_URL}/{endpoint}"
    
    # Data front-end mapping for API payload (snake_case)
    payload = {}
    if module == 'Tarefas':
        payload = {
            'descricao': data.get('Descrição'),
            'responsavel': data.get('Responsável'),
            # Data convert for ISO 8601 (String)
            'data_limite': data.get('Data Limite').isoformat(), 
            'status': data.get('Status'),
            'prioridade': data.get('Prioridade'),
            'observacoes': data.get('Observações', '')
        }
    # Adicionar lógica de payload para Contatos, Atas e Vendas aqui...

    try:
        if is_editing:
            # PUT for update
            url = f"{url}/{item_id}"
            response = requests.put(url, headers=get_api_headers(), json=payload)
            success_msg = f"{module.rstrip('s')} atualizada via API com sucesso!"
        else:
            # POST for create
            response = requests.post(url, headers=get_api_headers(), json=payload)
            success_msg = f"Nova {module.rstrip('s')} criada. n8n acionado!"
            
        response.raise_for_status()
        
        st.toast(success_msg, icon="👍")
        del st.session_state['data_cache'][module]  # Clear cache to refetch updated data
        st.rerun()

    except requests.exceptions.RequestException as e:
        error_detail = response.json().get('detail', str(e)) if 'response' in locals() and response.content else str(e)
        st.error(f"Erro ao Salvar na API: {error_detail}")