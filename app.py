import streamlit as st
import pandas as pd
import plotly.express as px
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from utils import carregar_dados

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Painel de Sífilis - Caucaia/CE",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS PERSONALIZADO (VISUAL INSTITUCIONAL)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #F1F5F9; }

    /* Atenua o efeito de "stale" durante o carregamento */
    div[data-testid="stStatusWidget"] { display: none; }
    div[data-testid="stDecoration"] { display: none; }
    .stSpinner > div { border-top-color: #1E3A8A !important; }

    /* Esconde a barra superior do Streamlit Cloud (mobile e desktop) */
    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    footer {
        display: none !important;
        visibility: hidden !important;
    }
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    /* Reduz o espaço em branco no topo */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }

    .header-institucional {
        background: linear-gradient(90deg, #1E3A8A 0%, #2563EB 100%);
        padding: 24px 32px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 6px 16px rgba(30, 58, 138, 0.25);
    }
    .header-institucional h1 {
        color: white; font-size: 30px; margin: 0; font-weight: 700;
        letter-spacing: -0.3px;
    }
    .header-institucional p {
        color: #DBEAFE; margin: 8px 0 0 0; font-size: 14px;
    }

    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.15);
        border-color: #3B82F6;
    }
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #1E3A8A, #3B82F6, #60A5FA);
    }
    div[data-testid="stMetric"] label {
        color: #334155 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 36px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #CBD5E1;
    }
    section[data-testid="stSidebar"] h1 {
        color: #1E3A8A !important;
        font-size: 22px !important;
        font-weight: 800 !important;
    }

    h2, h3 {
        color: #1E3A8A !important;
        font-weight: 800 !important;
        padding-bottom: 8px;
        border-bottom: 3px solid #3B82F6;
        margin-top: 10px !important;
    }
    h2 { font-size: 22px !important; }
    h3 { font-size: 18px !important; }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #CBD5E1;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08);
    }

    .stButton > button, .stDownloadButton > button {
        background-color: #1E3A8A;
        color: white;
        border-radius: 8px;
        font-weight: 700;
        border: none;
        padding: 10px 20px;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #2563EB;
        transform: translateY(-1px);
    }

    hr {
        border-color: #CBD5E1 !important;
        margin: 30px 0 !important;
    }

    /* Ajustes para celular (responsividade) */
    @media (max-width: 768px) {
        .header-institucional {
            padding: 16px 20px;
        }
        .header-institucional h1 {
            font-size: 22px;
        }
        .header-institucional p {
            font-size: 12px;
        }
        div[data-testid="stMetric"] {
            padding: 15px 18px;
        }
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
            font-size: 28px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. AUTENTICAÇÃO (LGPD)
# ==========================================
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login(location='sidebar')

if st.session_state.get("authentication_status") is False:
    st.error('❌ Usuário ou senha incorretos. Tente novamente.')
    st.stop()

elif st.session_state.get("authentication_status") is None:
    st.warning('🔒 Faça login na barra lateral para acessar o painel completo.')

else:
    with st.sidebar.expander("🔐 Minha Conta"):
        st.markdown(f"**Logado como:** {st.session_state['name']}")
        st.markdown(f"**Usuário:** `{st.session_state['username']}`")
        st.divider()
        st.markdown("**Trocar senha:**")
        try:
            if authenticator.reset_password(
                st.session_state['username'],
                location='sidebar'
            ):
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success('✅ Senha alterada com sucesso!')
        except Exception as e:
            st.error(f"Erro ao alterar senha: {e}")

    authenticator.logout('🚪 Sair', 'sidebar')

# ==========================================
# 4. CARREGAMENTO DOS DADOS
# ==========================================
@st.cache_data(ttl=600, show_spinner=False)
def load():
    return carregar_dados()

with st.spinner("📊 Carregando dados do SINAN..."):
    try:
        adq, cong, gest = load()
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        st.stop()

# ==========================================
# 5. FUNÇÃO PARA DECODIFICAR IDADE (SINAN)
# ==========================================
def decodificar_idade(valor):
    if pd.isna(valor):
        return None
    try:
        s = str(int(float(valor)))
        if len(s) < 4:
            s = s.zfill(4)
        unidade = s[0]
        quantidade = int(s[1:4])
        if unidade == '4':
            return quantidade
        return None
    except (ValueError, TypeError):
        return None

# ==========================================
# 5.1. FUNÇÃO PARA APLICAR TEMA PROFISSIONAL AOS GRÁFICOS
# ==========================================
def aplicar_tema_profissional(fig, altura=380):
    fig.update_layout(
        height=altura,
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        font=dict(family="Inter, -apple-system, sans-serif", size=13, color='#1E293B'),
        title=dict(font=dict(size=16, color='#0F172A'), x=0.02, xanchor='left'),
        margin=dict(l=20, r=20, t=50, b=40),
        hoverlabel=dict(bgcolor='#1E3A8A', font_size=13, font_family="Inter", font_color='white')
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor='#94A3B8',
        linewidth=1.5,
        tickfont=dict(size=11, color='#334155'),
        title_font=dict(size=13, color='#1E3A8A')
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor='#E2E8F0',
        gridwidth=1,
        linecolor='#94A3B8',
        linewidth=1.5,
        tickfont=dict(size=11, color='#334155'),
        title_font=dict(size=13, color='#1E3A8A')
    )
    return fig

# ==========================================
# 6. BARRA LATERAL (FILTROS)
# ==========================================
st.sidebar.markdown("---")
st.sidebar.title("Filtros do Painel")

tipo_sifilis = st.sidebar.selectbox(
    "Tipo de Sífilis",
    ["Sífilis Adquirida", "Sífilis Congênita", "Sífilis em Gestante"],
    key="filtro_tipo"
)

# ==========================================
# 7. SELEÇÃO DO DATAFRAME
# ==========================================
if tipo_sifilis == "Sífilis Adquirida":
    df = adq.copy()
    titulo_painel = "Painel de Sífilis Adquirida"
elif tipo_sifilis == "Sífilis Congênita":
    df = cong.copy()
    titulo_painel = "Painel de Sífilis Congênita"
else:
    if gest is not None:
        df = gest.copy()
        titulo_painel = "Painel de Sífilis em Gestante"
    else:
        st.sidebar.warning("Dados de Gestante não carregados.")
        df = pd.DataFrame()
        titulo_painel = "Painel de Sífilis em Gestante"

if "tipo_anterior" not in st.session_state:
    st.session_state.tipo_anterior = tipo_sifilis

if st.session_state.tipo_anterior != tipo_sifilis:
    st.session_state.tipo_anterior = tipo_sifilis
    for k in ["filtro_sexo", "filtro_raca", "filtro_anos", "filtro_escolaridade"]:
        st.session_state.pop(k, None)
    st.rerun()

# ==========================================
# 8. FILTROS DINÂMICOS
# ==========================================
if not df.empty and 'Ano' in df.columns:
    anos_disponiveis = sorted(df['Ano'].dropna().unique().tolist())
    anos_selecionados = st.sidebar.multiselect(
        "Selecione o(s) Ano(s)", options=anos_disponiveis,
        default=anos_disponiveis, key="filtro_anos"
    )
    if len(anos_selecionados) == 0:
        st.warning("⚠️ Selecione pelo menos um ano.")
        st.stop()
    df = df[df['Ano'].isin(anos_selecionados)]

if not df.empty and 'CS_SEXO' in df.columns:
    sexos_disponiveis = sorted(df['CS_SEXO'].dropna().astype(str).unique().tolist())
    sexos_selecionados = st.sidebar.multiselect(
        "Selecione o(s) Sexo(s)", options=sexos_disponiveis,
        default=sexos_disponiveis, key="filtro_sexo"
    )
    if len(sexos_selecionados) == 0:
        st.warning("⚠️ Selecione pelo menos um sexo.")
        st.stop()
    df = df[df['CS_SEXO'].astype(str).isin(sexos_selecionados)]

if not df.empty and 'CS_RACA' in df.columns:
    racas_disponiveis = sorted(df['CS_RACA'].dropna().astype(str).unique().tolist())
    racas_selecionadas = st.sidebar.multiselect(
        "Selecione a(s) Raça(s)/Cor(es)", options=racas_disponiveis,
        default=racas_disponiveis, key="filtro_raca"
    )
    if len(racas_selecionadas) == 0:
        st.warning("⚠️ Selecione pelo menos uma raça/cor.")
        st.stop()
    df = df[df['CS_RACA'].astype(str).isin(racas_selecionadas)]

if not df.empty and 'CS_ESCOL_N' in df.columns:
    escol_disponiveis = sorted(df['CS_ESCOL_N'].dropna().astype(str).unique().tolist())
    escol_selecionadas = st.sidebar.multiselect(
        "Selecione a(s) Escolaridade(s)", options=escol_disponiveis,
        default=escol_disponiveis, key="filtro_escolaridade"
    )
    if len(escol_selecionadas) == 0:
        st.warning("⚠️ Selecione pelo menos uma escolaridade.")
        st.stop()
    df = df[df['CS_ESCOL_N'].astype(str).isin(escol_selecionadas)]

# ==========================================
# 9. CONTEÚDO PRINCIPAL
# ==========================================
st.markdown(f"""
<div class="header-institucional">
    <h1>📊 {titulo_painel}</h1>
    <p>Vigilância Epidemiológica • Caucaia/CE • Dados do SINAN (2021-2026)</p>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("Nenhum dado disponível para os filtros selecionados.")
    st.stop()

# --- Métricas ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Notificações", f"{len(df):,}".replace(",", "."))
with col2:
    if 'Ano' in df.columns and not df['Ano'].isna().all():
        st.metric("Ano Mais Recente", int(df['Ano'].max()))
with col3:
    if 'CS_SEXO' in df.columns:
        sexo_str = df['CS_SEXO'].astype(str).str.lower().str.strip()
        fem = len(df[sexo_str.isin(['f', 'feminino', '2', '2.0'])])
        st.metric("Casos em Mulheres", f"{fem:,}".replace(",", "."))

col4, col5 = st.columns(2)
with col4:
    if 'CS_RACA' in df.columns:
        raca_str = df['CS_RACA'].astype(str).str.lower().str.strip()
        ign = len(df[raca_str.isin(['ignorado', '9', '9.0'])])
        st.metric("Raça Ignorada", f"{ign:,}".replace(",", "."))
with col5:
    if 'Ano' in df.columns:
        casos_por_ano = df.groupby('Ano').size().sort_index()
        if len(casos_por_ano) >= 2:
            ultimo_ano = casos_por_ano.index[-1]
            ano_anterior = casos_por_ano.index[-2]
            casos_ultimo = casos_por_ano.iloc[-1]
            casos_anterior = casos_por_ano.iloc[-2]
            if casos_anterior > 0:
                variacao = ((casos_ultimo - casos_anterior) / casos_anterior) * 100
                st.metric(
                    f"Variação {int(ultimo_ano)} vs {int(ano_anterior)}",
                    f"{variacao:+.1f}%",
                    delta=f"{casos_ultimo - casos_anterior:+d} casos"
                )

st.divider()

# ==========================================
# 10. GRÁFICOS
# ==========================================
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("Evolução Temporal (Mensal)")
    if 'Ano' in df.columns and 'Mes' in df.columns:
        df_tempo = df.groupby(['Ano', 'Mes']).size().reset_index(name='Casos')
        df_tempo['Data'] = pd.to_datetime(
            df_tempo['Ano'].astype(str) + '-' + df_tempo['Mes'].astype(str) + '-01'
        )
        df_tempo = df_tempo.sort_values('Data')

        fig_linha = px.area(
            df_tempo, x='Data', y='Casos',
            title=f"Casos por Mês - {tipo_sifilis}",
            markers=True,
            color_discrete_sequence=['#1E3A8A']
        )

        fig_linha.update_traces(
            line=dict(width=3, color='#1E3A8A'),
            marker=dict(size=6, color='#1E3A8A',
                        line=dict(width=1.5, color='white')),
            fillcolor='rgba(30, 58, 138, 0.15)',
            hovertemplate='<b>%{x|%b/%Y}</b><br>Casos: %{y}<extra></extra>'
        )

        fig_linha.update_xaxes(
            tickmode='auto',
            nticks=8,
            tickformat="%b/%y",
            tickangle=-30,
            tickfont=dict(size=10, color='#334155'),
            showgrid=False,
            title=""
        )

        fig_linha.update_yaxes(
            showgrid=True,
            gridcolor='#E2E8F0',
            gridwidth=1,
            title="Casos notificados",
            tickfont=dict(size=11, color='#334155')
        )

        fig_linha = aplicar_tema_profissional(fig_linha, altura=420)

        fig_linha.update_xaxes(
            tickmode='auto',
            nticks=8,
            tickformat="%b/%y",
            tickangle=-30,
            tickfont=dict(size=10, color='#334155'),
            showgrid=False,
            title=""
        )

        fig_linha.update_layout(
            margin=dict(l=20, r=20, t=60, b=70)
        )

        st.plotly_chart(fig_linha, use_container_width=True, key=f"linha_{tipo_sifilis}")
    else:
        st.info("Colunas de Ano/Mês não encontradas.")

with col_graf2:
    st.subheader("Distribuição por Raça/Cor")
    if 'CS_RACA' in df.columns:
        df_raca = df['CS_RACA'].value_counts().reset_index()
        df_raca.columns = ['Raça/Cor', 'Casos']
        fig_raca = px.pie(
            df_raca, names='Raça/Cor', values='Casos', hole=0.5,
            title=f"Proporção por Raça/Cor - {tipo_sifilis}",
            color_discrete_sequence=['#1E3A8A', '#3B82F6', '#60A5FA',
                                     '#F59E0B', '#EF4444', '#10B981', '#8B5CF6']
        )
        fig_raca.update_traces(
            textposition='outside',
            textinfo='percent+label',
            textfont=dict(size=12, color='#1E293B'),
            marker=dict(line=dict(color='white', width=2))
        )
        fig_raca = aplicar_tema_profissional(fig_raca)
        st.plotly_chart(fig_raca, use_container_width=True, key=f"pizza_{tipo_sifilis}")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.subheader("Distribuição por Sexo")
    if 'CS_SEXO' in df.columns:
        df_sexo = df['CS_SEXO'].value_counts().reset_index()
        df_sexo.columns = ['Sexo', 'Casos']
        fig_sexo = px.bar(
            df_sexo, x='Sexo', y='Casos',
            title=f"Casos por Sexo - {tipo_sifilis}",
            color='Sexo', text_auto=True,
            color_discrete_sequence=['#1E3A8A', '#F59E0B']
        )
        fig_sexo.update_traces(
            textfont=dict(size=14, color='white'),
            textposition='inside',
            marker=dict(line=dict(color='white', width=1.5))
        )
        fig_sexo.update_layout(showlegend=False)
        fig_sexo = aplicar_tema_profissional(fig_sexo)
        st.plotly_chart(fig_sexo, use_container_width=True, key=f"sexo_{tipo_sifilis}")

with col_graf4:
    st.subheader("Faixa Etária (em anos)")
    if 'NU_IDADE_N' in df.columns:
        df_idade = df.copy()
        df_idade['IDADE_ANOS'] = df_idade['NU_IDADE_N'].apply(decodificar_idade)
        df_idade = df_idade.dropna(subset=['IDADE_ANOS'])
        if not df_idade.empty:
            bins = [0, 10, 20, 30, 40, 50, 60, 120]
            labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60+']
            df_idade['Faixa_Etaria'] = pd.cut(
                df_idade['IDADE_ANOS'], bins=bins, labels=labels, right=False
            )
            df_faixa = df_idade['Faixa_Etaria'].value_counts().reset_index()
            df_faixa.columns = ['Faixa Etária', 'Casos']
            df_faixa = df_faixa.sort_values('Faixa Etária')
            fig_idade = px.bar(
                df_faixa, x='Faixa Etária', y='Casos',
                title=f"Casos por Faixa Etária - {tipo_sifilis}",
                color='Faixa Etária', text_auto=True,
                color_discrete_sequence=['#1E3A8A', '#1E40AF', '#2563EB',
                                         '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
            )
            fig_idade.update_traces(
                textfont=dict(size=12, color='white'),
                textposition='inside',
                marker=dict(line=dict(color='white', width=1.5))
            )
            fig_idade.update_layout(showlegend=False)
            fig_idade = aplicar_tema_profissional(fig_idade)
            st.plotly_chart(fig_idade, use_container_width=True, key=f"idade_{tipo_sifilis}")

col_graf5, col_graf6 = st.columns(2)

with col_graf5:
    st.subheader("📊 Evolução Anual")
    if 'Ano' in df.columns:
        df_anual = df.groupby('Ano').size().reset_index(name='Casos')
        df_anual = df_anual.sort_values('Ano')
        fig_anual = px.bar(
            df_anual, x='Ano', y='Casos',
            title=f"Total de Casos por Ano - {tipo_sifilis}",
            color='Ano', text_auto=True,
            color_discrete_sequence=['#1E3A8A', '#1E40AF', '#2563EB',
                                     '#3B82F6', '#60A5FA', '#93C5FD']
        )
        fig_anual.update_traces(
            textfont=dict(size=14, color='white'),
            textposition='inside',
            marker=dict(line=dict(color='white', width=1.5))
        )
        fig_anual.update_layout(showlegend=False)
        fig_anual = aplicar_tema_profissional(fig_anual)
        st.plotly_chart(fig_anual, use_container_width=True, key=f"anual_{tipo_sifilis}")

with col_graf6:
    st.subheader("🎓 Distribuição por Escolaridade")
    if 'CS_ESCOL_N' in df.columns:
        df_esc = df['CS_ESCOL_N'].value_counts().reset_index()
        df_esc.columns = ['Escolaridade', 'Casos']
        df_esc = df_esc.sort_values('Casos', ascending=True)
        fig_esc = px.bar(
            df_esc, x='Casos', y='Escolaridade',
            title=f"Casos por Escolaridade - {tipo_sifilis}",
            orientation='h', text_auto=True,
            color='Casos',
            color_continuous_scale='Blues'
        )
        fig_esc.update_traces(
            textfont=dict(size=11, color='white'),
            textposition='inside',
            marker=dict(line=dict(color='white', width=1.5))
        )
        fig_esc.update_layout(coloraxis_showscale=False)
        fig_esc = aplicar_tema_profissional(fig_esc, altura=420)
        st.plotly_chart(fig_esc, use_container_width=True, key=f"escol_{tipo_sifilis}")

# ==========================================
# 11. TABELA DE DADOS (PROTEGIDA POR LOGIN - LGPD)
# ==========================================
st.divider()

if st.session_state.get("authentication_status"):
    st.subheader("📋 Visualização dos Dados Brutos")
    st.info(f"🔓 Acesso autorizado para: **{st.session_state['name']}**")
    st.dataframe(df.head(100), use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar dados filtrados (CSV)",
        data=csv,
        file_name=f'{tipo_sifilis.lower().replace(" ", "_")}_filtrado.csv',
        mime='text/csv',
    )
else:
    st.subheader("📋 Visualização dos Dados Brutos")
    st.warning(
        "🔒 **Acesso restrito (LGPD).**\n\n"
        "Os dados brutos contêm informações pessoais e só podem ser visualizados "
        "após autenticação. Faça login na barra lateral com seu usuário institucional."
    )
