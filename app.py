import streamlit as st
import pandas as pd
import os
from logic import (
    gerar_resposta_ai, 
    detectar_cabecalho, 
    auditoria_dados, 
    preparar_contexto_seguro
)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="DHL LogiScan & CoPilot V6", layout="wide", page_icon="📦")

# --- ESTILIZAÇÃO DHL (JANDIRA V6.3 - FINAL REFINADO) ---
st.markdown("""
    <style>
    /* Fundo da tela central em Amarelo DHL */
    .stApp { 
        background-color: #FFCC00; 
    }
    
    /* Sidebar: Vermelho DHL com texto Branco */
    [data-testid="stSidebar"] { 
        background-color: #D40511 !important; 
    }
    [data-testid="stSidebar"] * { 
        color: white !important; 
    }
    
    /* Tela Central: Regra Geral - PRETO e NEGRITO */
    h1, h2, h3, p, label, .stMarkdown { 
        color: #000000 !important; 
        font-family: 'Arial', sans-serif;
        font-weight: bold !important;
    }

    /* EXCEÇÃO: Botão 'Gerar Solução' - FUNDO VERMELHO / LETRA BRANCA */
    div.stButton > button { 
        background-color: #D40511 !important; 
        color: #ffffff !important; /* Branco para contraste total */
        font-weight: bold !important; 
        border-radius: 5px; 
        border: 2px solid #ffffff; 
        width: 100%; /* Opcional: deixa o botão mais imponente */
        height: 3em;
    }
    
    /* Garantindo que o texto dentro do botão seja branco mesmo no hover */
    div.stButton > button div p {
        color: #ffffff !important;
    }

    /* CAIXA DE UPLOAD: Fundo branco e letras pretas */
    [data-testid="stFileUploaderDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #D40511 !important;
    }
    [data-testid="stFileUploaderDropzone"] div div span {
        color: #000000 !important;
    }

    /* Ajuste para as caixas de texto (Inputs) */
    .stTextArea textarea, .stTextInput input {
        background-color: #ffffff !important;
        color: #000000 !important;
        font-weight: bold !important;
    }
    
    .status-box { 
        padding: 15px; 
        border-radius: 5px; 
        background-color: #ffffff; 
        border-left: 8px solid #D40511; 
        margin-bottom: 20px;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR E NAVEGAÇÃO (HIERARQUIA CORRIGIDA) ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/DHL_Logo.svg/1200px-DHL_Logo.svg.png", width=180)
    st.markdown("---")
    st.markdown("### 🛠️ Painel de Controle")
    aba = st.radio("Selecione a Ferramenta:", 
                   ["🚀 Assistente de IA (V5)", "🔍 Auditor de Dados (V6)", "📊 Dashboard Admin"])
    
    st.markdown("---")
    # Inversão de papéis conforme solicitado pelo Arquiteto Jadiel
    st.write("**Arquiteto/Mentor:** Jadiel")
    st.write("**Copiloto Técnico:** Google Gemini")
    st.success("Conexão Gemini API: Ativa ✅")

# --- INICIALIZAÇÃO DE ESTADO ---
if 'contexto_planilha' not in st.session_state:
    st.session_state.contexto_planilha = "Nenhuma planilha carregada."

# --- ABA 1: ASSISTENTE DE IA ---
if aba == "🚀 Assistente de IA (V5)":
    st.title("🚀 DHL Excel Assistant V6.0")
    st.markdown("""
    <div class='status-box'>
    <b>Protocolo de Privacidade Ativo:</b> As perguntas são processadas anonimamente. 
    Se uma planilha for carregada na Aba Auditor, eu utilizarei a estrutura dela para te ajudar.
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        user_input = st.text_area("Descreva sua necessidade (Ex: Como calcular o frete peso médio?):", placeholder="Digite aqui...")
        
        col1, col2 = st.columns([1, 4])
        if col1.button("Gerar Solução"):
            if user_input:
                with st.spinner("IA Analisando requisitos logísticos..."):
                    # Usa o contexto da planilha se houver, garantindo respostas precisas
                    resposta = gerar_resposta_ai(user_input, st.session_state.contexto_planilha)
                    st.markdown("---")
                    st.markdown(resposta)
            else:
                st.warning("Por favor, digite uma dúvida antes de consultar.")

# --- ABA 2: AUDITOR DE DADOS ---
elif aba == "🔍 Auditor de Dados (V6)":
    st.title("🔍 Auditoria V6 - Scanner de Integridade")
    st.write("Suba sua base de dados para análise de consistência e limpeza de metadados.")
    
    arquivo = st.file_uploader("Arraste seu arquivo Excel (.xlsx)", type=["xlsx"])
    
    if arquivo:
        # 1. Detecta cabeçalho automaticamente (Logic)
        skip = detectar_cabecalho(arquivo)
        df = pd.read_excel(arquivo, skiprows=skip)
        
        # 2. Atualiza o contexto de privacidade (Logic)
        st.session_state.contexto_planilha = preparar_contexto_seguro(df)
        
        st.info(f"✅ Arquivo processado. Cabeçalho identificado na linha {skip + 1}.")
        st.dataframe(df.head(5), use_container_width=True)
        
        if st.button("Executar Scan de Erros"):
            with st.spinner("Auditando..."):
                lista_erros = auditoria_dados(df)
                if lista_erros:
                    st.subheader("⚠️ Inconsistências Detectadas")
                    for erro in lista_erros:
                        st.error(erro)
                else:
                    st.success("SLA de Integridade mantido: Nenhum erro estrutural detectado.")

# --- ABA 3: DASHBOARD ADMIN ---
elif aba == "📊 Dashboard Admin":
    st.title("📊 Monitor de Performance") # <--- Removido o (REMAR View)
    st.write("Análise de gaps de conhecimento e recorrência de dúvidas da equipe.")
    # ... restante do código permanece igual

    log_path = "uso_copilot_log.csv"
    if os.path.exists(log_path):
        df_log = pd.read_csv(log_path)
        
        # Métricas de Gestão
        m1, m2, m3 = st.columns(3)
        m1.metric("Consultas Totais", len(df_log))
        
        if "Nível" in df_log.columns:
            # Pega o nível mais frequente
            nivel_frequente = df_log["Nível"].mode()[0]
            m2.metric("Nível de Complexidade", nivel_frequente)
            
            # Gráfico Simples
            st.write("#### Distribuição de Conhecimento")
            st.bar_chart(df_log["Nível"].value_counts())

        st.markdown("---")
        st.write("#### Log de Atividades Recentes")
        st.table(df_log.tail(10))
        
        # Exportação para a Isa
        csv = df_log.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Relatório de Gaps (CSV)", csv, "relatorio_desenvolvimento_equipe.csv", "text/csv")
    else:
        st.info("Aguardando primeiras interações para gerar indicadores.")