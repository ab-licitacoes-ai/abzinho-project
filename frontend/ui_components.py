import streamlit as st
from datetime import datetime
from .config import TEAM_MEMBERS, STATUS_TAREFAS, STATUS_CONTATOS, STATUS_ATAS, STATUS_VENDAS, PRIORIDADES, MODULES, MODULE_ICONS
from .data_manager import handle_save_api, clean_currency, fetch_data_from_api 

# --- Funções de Renderização de Páginas de Autenticação ---

def render_login():
    """Renderiza a página de Login e tenta autenticar via API."""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # Layout Card
        st.markdown("""<div style="background-color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 10vh;">""", unsafe_allow_html=True)
        st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><h1 style="font-size: 24px; font-weight: bold; color: #1f2937;">Acesso ao Portal ABzinho</h1></div>""", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("E-mail", placeholder="seu.email@ablicitacoes.com.br")
            password = st.text_input("Senha", type="password", placeholder="••••••••")
            login_button = st.form_submit_button("Entrar", use_container_width=True)

            if login_button:
                # SIMULAÇÃO DA CHAMADA À API
                import requests
                from .config import API_BASE_URL 
                
                login_url = f"{API_BASE_URL}/auth/login"
                try:
                    response = requests.post(login_url, json={"email": email, "password": password})
                    if response.status_code == 200:
                        token_data = response.json()
                        st.session_state['auth_token'] = token_data.get('access_token')
                        st.session_state['logged_in'] = True
                        st.session_state['page'] = 'dashboard'
                        st.session_state['current_user'] = email.split('@')[0].capitalize()
                        st.toast("Login realizado com sucesso!", icon="✅")
                        st.rerun()
                    else:
                        st.error(response.json().get('detail', 'Credenciais inválidas ou erro desconhecido.'))
                except requests.exceptions.ConnectionError:
                    st.error("Erro de conexão com o Back-end da API.")
                
        st.markdown("""
            <p style="text-align: center; margin-top: 15px; font-size: 14px; color: #4b5563;">
                Novo por aqui? Crie sua conta.
            </p>
            </div>
            """, unsafe_allow_html=True)


def render_cadastro():
    """Renderiza a página de Cadastro."""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("""<div style="background-color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 10vh;">""", unsafe_allow_html=True)
        st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><h1 style="font-size: 24px; font-weight: bold; color: #1f2937;">Criação de Conta ABzinho</h1></div>""", unsafe_allow_html=True)
        
        with st.form("cadastro_form"):
            name = st.text_input("Nome Completo")
            email = st.text_input("E-mail Profissional")
            password = st.text_input("Senha", type="password")
            confirm_password = st.text_input("Confirmação de Senha", type="password")
            
            if password:
                st.progress(min(len(password) * 10, 100), text="Força da Senha")

            cadastro_button = st.form_submit_button("Criar Conta", use_container_width=True)

            if cadastro_button:
                if password != confirm_password:
                    st.error("As senhas não coincidem.")
                elif len(password) < 8:
                    st.warning("A senha deve ter no mínimo 8 caracteres.")
                else:
                    # Em produção: POST para /api/v1/users
                    st.toast("Conta criada! Faça login agora.", icon="🎉")
                    st.session_state['page'] = 'login'
                    st.rerun()
        
        st.markdown(f"""
            <p style="text-align: center; margin-top: 15px; font-size: 14px; color: #4b5563;">
                Já tem conta? <a href="#" onclick="window.parent.document.querySelector('[data-testid=\"stButton\"].to_login').click()" style="color: #2563eb; font-weight: 500;">Fazer Login.</a>
            </p>
            </div>
            """, unsafe_allow_html=True)


def render_sidebar():
    """Renderiza a navegação lateral."""
    st.sidebar.markdown(f'<h1 class="css-h3">ABzinho Portal</h1>', unsafe_allow_html=True)
    st.sidebar.markdown(f"**Usuário:** {st.session_state['current_user']}")
    st.sidebar.markdown("---")
    
    for module in MODULES:
        icon = MODULE_ICONS[module]
        if st.session_state['active_module'] == module:
            st.sidebar.markdown(f'<a href="#" style="background-color: #2563eb; color: white; padding: 10px; border-radius: 8px; display: block; margin-bottom: 5px;">{icon} {module}</a>', unsafe_allow_html=True)
        else:
            if st.sidebar.button(f"{icon} {module}", key=f"nav_{module}", use_container_width=True):
                st.session_state['active_module'] = module
                st.session_state['edit_mode'] = False
                st.session_state['show_modal'] = False
                st.rerun()
        
    st.sidebar.markdown("---")
    st.sidebar.button("Sair", key="logout_btn", on_click=lambda: (st.session_state.update({'logged_in': False, 'page': 'login', 'auth_token': None}), st.toast("Sessão encerrada.", icon="👋"), st.rerun()), use_container_width=True)


def render_crud_form(is_editing=False, item_to_edit=None):
    """Renderiza o formulário de Criação/Edição em um contêiner."""
    module = st.session_state['active_module']
    title = f"{'Editar' if is_editing else 'Criar Nova'} {module.rstrip('s')}"
    
    # Mapeamento de campos (apenas o de Tarefas está mapeado para a API de exemplo)
    field_map = {
        'Tarefas': [('Descrição', st.text_area, None), ('Responsável', st.selectbox, TEAM_MEMBERS), ('Data Limite', st.date_input, None), ('Status', st.selectbox, STATUS_TAREFAS), ('Prioridade', st.selectbox, PRIORIDADES), ('Observações', st.text_area, None)],
        'Contatos': [('Pessoa/Órgão', st.text_input, None), ('Motivo', st.text_input, None), ('Data Follow-up', st.date_input, None), ('Responsável', st.selectbox, TEAM_MEMBERS), ('Status', st.selectbox, STATUS_CONTATOS), ('Prioridade', st.selectbox, PRIORIDADES)],
        'Atas': [('Órgão/Entidade', st.text_input, None), ('Objeto/Itens', st.text_input, None), ('Valor Utilizado (R$)', st.number_input, None), ('Vigência Final', st.date_input, None), ('Status', st.selectbox, STATUS_ATAS), ('Prioridade', st.selectbox, PRIORIDADES)],
        'Vendas': [('Tipo', st.selectbox, ['Licitação', 'Entrega Direta', 'Assessoria']), ('Cliente/Órgão', st.text_input, None), ('Valor Total (R$)', st.number_input, None), ('Data da Venda', st.date_input, None), ('Responsável', st.selectbox, TEAM_MEMBERS), ('Status', st.selectbox, STATUS_VENDAS)],
    }
    form_fields = field_map.get(module, [])
    
    with st.container(border=True):
        st.subheader(title)
        
        with st.form(key=f"crud_form_{module}_{item_to_edit['ID'].iloc[0] if is_editing and item_to_edit is not None else 'new'}"):
            form_data = {}
            
            for label, widget, options in form_fields:
                # Prepara o valor padrão para edição
                default_value = item_to_edit[label].iloc[0] if is_editing and item_to_edit is not None and label in item_to_edit.columns else None
                cleaned_value = clean_currency(default_value) if widget == st.number_input else default_value
                
                if widget == st.selectbox:
                    # Encontra o índice da opção salva
                    index = options.index(cleaned_value) if is_editing and cleaned_value in options else 0
                    form_data[label] = widget(label, options=options, index=index)
                elif widget == st.date_input:
                    # Converte string/datetime para date
                    if is_editing and isinstance(cleaned_value, (str, datetime)):
                        try:
                            value = datetime.fromisoformat(cleaned_value).date()
                        except ValueError:
                            value = datetime.today().date()
                    elif is_editing and isinstance(cleaned_value, date):
                         value = cleaned_value
                    else:
                        value = datetime.today().date()
                    form_data[label] = widget(label, value=value)
                elif widget == st.number_input:
                    form_data[label] = widget(label, min_value=0.0, value=cleaned_value if cleaned_value is not None else 0.0, format="%.2f")
                else: 
                    form_data[label] = widget(label, value=cleaned_value if cleaned_value else "")

            col_save, col_cancel = st.columns([1, 1])
            with col_save:
                save_button = st.form_submit_button(f"{'Salvar' if is_editing else 'Criar'} {module.rstrip('s')}", use_container_width=True)
            with col_cancel:
                cancel_button = st.form_submit_button("Cancelar", type="secondary", use_container_width=True)

            if save_button:
                item_id = item_to_edit['ID'].iloc[0] if is_editing and item_to_edit is not None else None
                handle_save_api(form_data, is_editing, item_id)
            
            if cancel_button:
                st.session_state['edit_mode'] = False
                st.session_state['show_modal'] = False
                st.rerun()


def render_dashboard_content():
    """Renderiza a área principal de listagem (CRUD List)."""
    module = st.session_state['active_module']
    
    # Chama a API
    df = fetch_data_from_api(module) 

    st.header(f"Gestão de {module}")
    st.markdown("---")
    
    # Lógica de Edição/Criação
    if st.session_state.get('edit_mode', False) and 'edit_item' in st.session_state:
        # Busca o item completo pelo ID (simulado, em produção usaria um endpoint GET /tasks/{id})
        item_data = df[df['ID'] == st.session_state['edit_item']['ID']]
        if not item_data.empty:
            render_crud_form(is_editing=True, item_to_edit=item_data)
            return

    # --- 1. Botões de Ação e Busca ---
    col_search, col_action = st.columns([3, 1])
    
    # ... (Lógica de busca e botão de Nova Tarefa) ...
    # Simplicidade para não repetir código
    
    # --- 2. Listagem de Dados ---
    st.subheader("Lista de Registros")
    
    if df.empty:
        st.info(f"Nenhum registro encontrado em {module} ou falha na conexão com a API.")
        # Botão Nova Tarefa (simulado)
        with col_action:
             if st.button(f"➕ Nova {module.rstrip('s')}", use_container_width=True, key="new_item_btn"):
                st.session_state['show_modal'] = True 
                st.rerun()
        if st.session_state.get('show_modal', False):
            st.markdown("---")
            render_crud_form(is_editing=False)
        return

    # Mapeamento de colunas para Streamlit (deve bater com o DataFrame após o data_manager)
    if module == 'Tarefas':
        cols_to_display = ['Descrição', 'Responsável', 'Data Limite', 'Status', 'Prioridade']
        col_ratios = [4, 2, 2, 2, 1]
    # ... (Mapeamento para Contatos, Atas, Vendas) ...
    else:
        cols_to_display = df.columns.drop('ID', errors='ignore').tolist()
        col_ratios = [len(cols_to_display)] * len(cols_to_display)
        
    final_col_ratios = [0.1] + col_ratios + [0.5]
    
    # Renderiza o cabeçalho (omitido por brevidade no código, mas existe no original)

    # Renderiza Linhas de Dados
    for index, row in df.iterrows():
        priority_class = f"priority-{row.get('Prioridade', 'low').lower()}"
        
        st.markdown(f'<div class="{priority_class}">', unsafe_allow_html=True)
        cols = st.columns(final_col_ratios, gap="small") 
        
        # Coluna 1 (Debug ID)
        cols[0].markdown(f'<span style="font-size: 8px; color: #ccc;">{str(row["ID"])[:4]}...</span>', unsafe_allow_html=True)
        
        # Coluna 2 (Descrição) - Alinhado à esquerda
        cols[1].markdown(f'**{row[cols_to_display[0]]}**', unsafe_allow_html=True)
        
        # Demais Colunas (Alinhadas ao Centro Vertical e Horizontalmente)
        for i, col_name in enumerate(cols_to_display):
            if i > 0:
                value = row[col_name]
                if col_name == 'Prioridade':
                    value = f'<span class="priority-strip-{str(value).lower()}">{value}</span>'
                
                cols[i+1].markdown(f'<div style="width: 100%; text-align: center;">{value}</div>', unsafe_allow_html=True)

        # Coluna Ação (Editar)
        edit_button = cols[-1].button("✏️", key=f"edit_{row['ID']}", help="Editar Item")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<hr style="margin-top: 5px; margin-bottom: 5px;">', unsafe_allow_html=True)

        if edit_button:
            st.session_state['edit_item'] = row
            st.session_state['edit_mode'] = True
            st.rerun()

    # Botão Nova Tarefa (simulado)
    with col_action:
         if st.button(f"➕ Nova {module.rstrip('s')}", use_container_width=True, key="new_item_btn_bottom"):
            st.session_state['show_modal'] = True 
            st.rerun()
    if st.session_state.get('show_modal', False):
        st.markdown("---")
        render_crud_form(is_editing=False)
