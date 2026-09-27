import streamlit as st
import pandas as pd
import plotly.express as px
from utils import carregar_dados

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Painel de Sífilis - SINAN",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CARREGAMENTO DOS DADOS
# ==========================================
@st.cache_data(show_spinner="Carregando dados do SINAN...")
def load():
    return carregar_dados()

try:
    adq, cong, gest = load()
except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    st.stop()

# ==========================================
# 3. FUNÇÃO PARA DECODIFICAR IDADE (SINAN)
# ==========================================
def decodificar_idade(valor):
    """Decodifica NU_IDADE_N do SINAN. Padrão: 4xxx = anos, 3xxx = meses."""
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
        else:
            return None
    except (ValueError, TypeError):
        return None

# ==========================================
# 4. BARRA LATERAL (Filtros)
# ==========================================
st.sidebar.title("Filtros do Painel")

tipo_sifilis = st.sidebar.selectbox(
    "Tipo de Sífilis",
    ["Sífilis Adquirida", "Sífilis Congênita", "Sífilis em Gestante"],
    key="filtro_tipo"
)

# ==========================================
# 5. SELEÇÃO DO DATAFRAME
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
# 6. FILTROS DINÂMICOS
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
# 7. CONTEÚDO PRINCIPAL
# ==========================================
st.title(f"📊 {titulo_painel}")
st.markdown("Análise de dados extraídos do SINAN (2021-2026).")

if df.empty:
    st.warning("Nenhum dado disponível para os filtros selecionados.")
    st.stop()

# --- Métricas (5 colunas) ---
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de Notificações", f"{len(df):,}".replace(",", "."))

with col2:
    if 'Ano' in df.columns and not df['Ano'].isna().all():
        st.metric("Ano Mais Recente", int(df['Ano'].max()))
    else:
        st.metric("Ano Mais Recente", "N/A")

with col3:
    if 'CS_SEXO' in df.columns:
        sexo_str = df['CS_SEXO'].astype(str).str.lower().str.strip()
        fem = len(df[sexo_str.isin(['f', 'feminino', '2', '2.0'])])
        st.metric("Casos em Mulheres", f"{fem:,}".replace(",", "."))
    else:
        st.metric("Casos em Mulheres", "N/A")

with col4:
    if 'CS_RACA' in df.columns:
        raca_str = df['CS_RACA'].astype(str).str.lower().str.strip()
        ign = len(df[raca_str.isin(['ignorado', '9', '9.0'])])
        st.metric("Raça Ignorada", f"{ign:,}".replace(",", "."))
    else:
        st.metric("Raça Ignorada", "N/A")

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
            else:
                st.metric("Variação Anual", "N/A")
        else:
            st.metric("Variação Anual", "N/A")
    else:
        st.metric("Variação Anual", "N/A")

st.divider()

# ==========================================
# 8. GRÁFICOS (Linha 1)
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
        fig_linha = px.line(
            df_tempo, x='Data', y='Casos',
            title=f"Casos por Mês - {tipo_sifilis}", markers=True
        )
        fig_linha.update_xaxes(dtick="M3", tickformat="%b\n%Y")
        st.plotly_chart(fig_linha, use_container_width=True, key=f"linha_{tipo_sifilis}")
    else:
        st.info("Colunas de Ano/Mês não encontradas.")

with col_graf2:
    st.subheader("Distribuição por Raça/Cor")
    if 'CS_RACA' in df.columns:
        df_raca = df['CS_RACA'].value_counts().reset_index()
        df_raca.columns = ['Raça/Cor', 'Casos']
        fig_raca = px.pie(
            df_raca, names='Raça/Cor', values='Casos', hole=0.4,
            title=f"Proporção por Raça/Cor - {tipo_sifilis}"
        )
        st.plotly_chart(fig_raca, use_container_width=True, key=f"pizza_{tipo_sifilis}")
    else:
        st.info("Coluna CS_RACA não encontrada.")

# ==========================================
# 9. GRÁFICOS (Linha 2)
# ==========================================
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.subheader("Distribuição por Sexo")
    if 'CS_SEXO' in df.columns:
        df_sexo = df['CS_SEXO'].value_counts().reset_index()
        df_sexo.columns = ['Sexo', 'Casos']
        fig_sexo = px.bar(
            df_sexo, x='Sexo', y='Casos',
            title=f"Casos por Sexo - {tipo_sifilis}",
            color='Sexo', text_auto=True
        )
        st.plotly_chart(fig_sexo, use_container_width=True, key=f"sexo_{tipo_sifilis}")
    else:
        st.info("Coluna CS_SEXO não encontrada.")

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
                color='Faixa Etária', text_auto=True
            )
            st.plotly_chart(fig_idade, use_container_width=True, key=f"idade_{tipo_sifilis}")
        else:
            st.info("Nenhuma idade em anos encontrada.")
    else:
        st.warning("⚠️ Coluna NU_IDADE_N não encontrada.")

# ==========================================
# 10. GRÁFICOS (Linha 3) - NOVOS
# ==========================================
col_graf5, col_graf6 = st.columns(2)

with col_graf5:
    st.subheader("📊 Evolução Anual (Total por Ano)")
    if 'Ano' in df.columns:
        df_anual = df.groupby('Ano').size().reset_index(name='Casos')
        df_anual = df_anual.sort_values('Ano')
        fig_anual = px.bar(
            df_anual, x='Ano', y='Casos',
            title=f"Total de Casos por Ano - {tipo_sifilis}",
            color='Ano', text_auto=True
        )
        fig_anual.update_layout(showlegend=False)
        st.plotly_chart(fig_anual, use_container_width=True, key=f"anual_{tipo_sifilis}")
    else:
        st.info("Coluna Ano não encontrada.")

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
            color='Casos', color_continuous_scale='Blues'
        )
        fig_esc.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_esc, use_container_width=True, key=f"escol_{tipo_sifilis}")
    else:
        st.info("Coluna CS_ESCOL_N não encontrada. Verifique se está no arquivo Excel.")

# ==========================================
# 11. TABELA E DOWNLOAD
# ==========================================
st.divider()
st.subheader("📋 Visualização dos Dados Brutos")
st.dataframe(df.head(100), use_container_width=True)

csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Baixar dados filtrados (CSV)",
    data=csv,
    file_name=f'{tipo_sifilis.lower().replace(" ", "_")}_filtrado.csv',
    mime='text/csv',
)