st.markdown("""
<style>
    /* Remove o aviso amarelo de "running" */
    div[data-testid="stStatusWidget"] {
        display: none;
    }
    
    /* Efeito de fade suave ao invés de esmaecer */
    .stApp [data-testid="stAppViewContainer"] {
        transition: opacity 0.3s ease;
    }
    
    /* Esconde o aviso amarelo de "app is running" */
    div[data-testid="stDecoration"] {
        display: none;
    }
    
    /* Cor do spinner de carregamento */
    .stSpinner > div {
        border-top-color: #1E3A8A !important;
    }
</style>
""", unsafe_allow_html=True)
