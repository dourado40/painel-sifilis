import pandas as pd
import os

# ==========================================
# CAMINHOS DOS ARQUIVOS
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_DADOS = os.path.join(BASE_DIR, 'dados')

# ==========================================
# DICIONÁRIOS DE DECODIFICAÇÃO (SINAN)
# ==========================================
MAPA_RACA = {
    1: 'Branca',
    2: 'Preta',
    3: 'Amarela',
    4: 'Parda',
    5: 'Indígena',
    9: 'Ignorado'
}

MAPA_SEXO = {
    'M': 'Masculino',
    'F': 'Feminino',
    'I': 'Ignorado',
    1: 'Masculino',
    2: 'Feminino',
    0: 'Ignorado'
}

MAPA_ESCOLARIDADE = {
    0: 'Analfabeto',
    1: '1ª a 4ª série incompleta',
    2: '4ª série completa',
    3: '5ª a 8ª série incompleta',
    4: 'Ensino fundamental completo',
    5: 'Ensino médio incompleto',
    6: 'Ensino médio completo',
    7: 'Educação superior incompleta',
    8: 'Educação superior completa',
    9: 'Ignorado',
    10: 'Não se aplica'
}

MAPA_GESTANTE = {
    1: '1º Trimestre',
    2: '2º Trimestre',
    3: '3º Trimestre',
    4: 'Idade gestacional ignorada',
    5: 'Não',
    6: 'Não se aplica',
    9: 'Ignorado'
}

# ==========================================
# FUNÇÕES AUXILIARES
# ==========================================

def _converter_datas(df, colunas):
    """Converte colunas específicas para o formato de data do Pandas."""
    for col in colunas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df


def _adicionar_tempo(df):
    """Adiciona colunas de Ano, Mês e Semana Epidemiológica baseadas na data de notificação."""
    if 'DT_NOTIFIC' in df.columns:
        df['Ano'] = df['DT_NOTIFIC'].dt.year
        df['Mes'] = df['DT_NOTIFIC'].dt.month
        # Semana epidemiológica (padrão aproximado do SINAN)
        df['Semana_Epidemiologica'] = df['DT_NOTIFIC'].dt.isocalendar().week
    return df


def _decodificar(df, incluir_gestante=False):
    """
    Traduz os códigos numéricos do SINAN para texto legível.
    """
    # --- Decodificar Raça/Cor ---
    if 'CS_RACA' in df.columns:
        df['CS_RACA'] = pd.to_numeric(df['CS_RACA'], errors='coerce')
        df['CS_RACA'] = df['CS_RACA'].map(MAPA_RACA).fillna('Ignorado')

    # --- Decodificar Sexo ---
    if 'CS_SEXO' in df.columns:
        # Converte para string maiúscula para padronizar (M, F, I)
        df['CS_SEXO'] = df['CS_SEXO'].astype(str).str.upper().str.strip()
        df['CS_SEXO'] = df['CS_SEXO'].map(MAPA_SEXO).fillna('Ignorado')

    # --- Decodificar Escolaridade ---
    if 'CS_ESCOL_N' in df.columns:
        df['CS_ESCOL_N'] = pd.to_numeric(df['CS_ESCOL_N'], errors='coerce')
        df['CS_ESCOL_N'] = df['CS_ESCOL_N'].map(MAPA_ESCOLARIDADE).fillna('Ignorado')

    # --- Decodificar Gestante (apenas para o dataframe de gestantes) ---
    if incluir_gestante and 'CS_GESTANT' in df.columns:
        df['CS_GESTANT'] = pd.to_numeric(df['CS_GESTANT'], errors='coerce')
        df['CS_GESTANT'] = df['CS_GESTANT'].map(MAPA_GESTANTE).fillna('Ignorado')

    return df


def _limpar_colunas(df):
    """Remove colunas completamente vazias."""
    return df.dropna(axis=1, how='all')


# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================

def carregar_dados(caminho_adq=None, caminho_cong=None, caminho_gest=None):
    """
    Carrega e processa os dados do SINAN.
    Retorna uma tupla: (adq, cong, gest)
    """

    # Caminhos padrão dos arquivos
    if caminho_adq is None:
        caminho_adq = os.path.join(PASTA_DADOS, 'sifadq2021_2026excel.xlsx')
    if caminho_cong is None:
        caminho_cong = os.path.join(PASTA_DADOS, 'sifcong2021_2026excel.xlsx')
    if caminho_gest is None:
        caminho_gest = os.path.join(PASTA_DADOS, 'sifgest2021_2026excel.xlsx')

    # --- PROCESSAMENTO ADQ (Sífilis Adquirida) ---
    adq = pd.read_excel(caminho_adq)
    adq = _limpar_colunas(adq)
    adq = _converter_datas(adq, [
        "DT_NOTIFIC", "DT_SIN_PRI", "DT_NASC",
        "DT_OBITO", "DT_ENCERRA", "DT_DIGITA"
    ])
    adq = _adicionar_tempo(adq)
    adq = _decodificar(adq, incluir_gestante=False)

    # --- PROCESSAMENTO CONG (Sífilis Congênita) ---
    cong = pd.read_excel(caminho_cong)
    cong = _limpar_colunas(cong)
    cong = _converter_datas(cong, [
        "DT_NOTIFIC", "DT_NASC", "DT_DIAG",
        "DT_OBITO", "DT_DIGITA", "DT_ENCERRA"
    ])
    cong = _adicionar_tempo(cong)
    cong = _decodificar(cong, incluir_gestante=False)

    # --- PROCESSAMENTO GEST (Gestante) ---
    gest = None
    if caminho_gest and os.path.exists(caminho_gest):
        gest = pd.read_excel(caminho_gest)
        gest = _limpar_colunas(gest)
        gest = _converter_datas(gest, [
            "DT_NOTIFIC", "DT_SIN_PRI", "DT_NASC",
            "DT_OBITO", "DT_ENCERRA", "DT_DIGITA"
        ])
        gest = _adicionar_tempo(gest)
        gest = _decodificar(gest, incluir_gestante=True)

    # Retorna os três dataframes
    return adq, cong, gest