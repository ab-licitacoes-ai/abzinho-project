import streamlit as st
from datetime import datetime

# Page configuration
PAGE_CONFIG = {
    "page_title": "Portal de Gestão ABzinho",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Data constants
TEAM_MEMBERS = ['Lucas', 'Dani', 'Bruno (Sócio)', 'Fabrício (Sócio)', 'Diego (Sócio)', 'ABzinho']
STATUS_TAREFAS = ['Pendente', 'Em Andamento', 'Concluída', 'Atrasada']
STATUS_CONTATOS = ['Aberto', 'Concluído', 'Atrasado', 'Follow-up Pendente']
STATUS_ATAS = ['Vigente', 'Vencendo (60d)', 'Uso Crítico', 'Expirada']
STATUS_VENDAS = ['Ganha', 'Perdida', 'Em Negociação']
PRIORIDADES = ['Alta', 'Média', 'Baixa']

# Modules and endpoints mapping
MODULES = ['Tarefas', 'Contatos', 'Atas', 'Vendas']
MODULE_ICONS = {'Tarefas': '📋', 'Contatos': '👥', 'Atas': '⚖️', 'Vendas': '📈'}

# Endpoint da API (Ajuste para o endereço real da sua VPS)
API_BASE_URL = "http://localhost:8000/api/v1" 

# CSS Style injections for streamlit
CSS_INJECTIONS = """
<style>
/* 1. Header e Sidebar */
.css-h3 { color: #2563eb; }
.stButton>button {
    background-color: #2563eb;
    color: white !important;
    border-radius: 8px;
    border: none;
    transition: all 0.2s;
}
.stButton>button:hover {
    background-color: #1d4ed8;
}

/* 2. Faixas de Prioridade (Simulação CSS em Streamlit) */
.priority-high { background-color: #fee2e2; border-left: 6px solid #ef4444; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
.priority-medium { background-color: #fffbe6; border-left: 6px solid #f59e0b; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
.priority-low { background-color: #eff6ff; border-left: 6px solid #3b82f6; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
.priority-strip-high { color: #ef4444; font-weight: bold; }
.priority-strip-medium { color: #f59e0b; font-weight: bold; }
.priority-strip-low { color: #3b82f6; font-weight: bold; }

/* 3. Correção do Alinhamento Vertical dos Dados nas Colunas */
.st-emotion-cache-1jm4edc > div {
    display: flex;
    align-items: center;
    height: 100%;
}
</style>
"""