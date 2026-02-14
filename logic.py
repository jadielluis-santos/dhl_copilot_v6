import pandas as pd
from google import genai
from google.genai import types
import streamlit as st
import datetime
import os

# --- CONFIGURAÇÃO DA API ---
def get_client():
    api_key = st.secrets["GEMINI_API_KEY"]
    return genai.Client(api_key=api_key)

# --- MOTOR DE INTELIGÊNCIA ---
def gerar_resposta_ai(pergunta, contexto_tabela=""):
    client = get_client()
    
    prompt_sistema = f"""
    Você é o Mentor Sênior de Logística da DHL. 
    Responda de forma pragmática e técnica.
    
    ESTRUTURA OBRIGATÓRIA DA RESPOSTA:
    1. NÍVEL: [Básico, Intermediário ou Avançado]
    2. EXPLICAÇÃO: [Explique o conceito por trás da dúvida]
    3. SOLUÇÃO: [Fórmula ou Código Python em bloco de código]
    4. DICA DE PRODUTIVIDADE: [Como automatizar isso para evitar trabalho manual]

    Contexto das Colunas da Planilha (Segurança Ativa):
    {contexto_tabela}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=prompt_sistema),
        contents=[pergunta]
    )
    
    texto_resposta = response.text
    
    # Extrai o nível para o log (tentativa simples de parsing)
    nivel = "Não Identificado"
    if "NÍVEL: Básico" in texto_resposta: nivel = "Básico"
    elif "NÍVEL: Intermediário" in texto_resposta: nivel = "Intermediário"
    elif "NÍVEL: Avançado" in texto_resposta: nivel = "Avançado"
    
    salvar_log_uso(pergunta, nivel)
    
    return texto_resposta

# --- FUNÇÕES DE APOIO E SEGURANÇA ---
def preparar_contexto_seguro(df):
    """Garante o compliance filtrando dados sensíveis."""
    info_colunas = [f"- {col} (Tipo: {df[col].dtype})" for col in df.columns]
    return "\n".join(info_colunas)

def detectar_cabecalho(file):
    file.seek(0)
    df_preview = pd.read_excel(file, nrows=20, header=None)
    file.seek(0)
    
    melhor_linha, max_preenchidos = 0, 0
    for i, row in df_preview.iterrows():
        preenchidos = row.count()
        if preenchidos > max_preenchidos:
            max_preenchidos, melhor_linha = preenchidos, i
    return melhor_linha

def auditoria_dados(df):
    erros = []
    nulos = df.isnull().sum().sum()
    if nulos > 0: erros.append(f"⚠️ {nulos} células vazias detectadas.")
    duplicados = df.duplicated().sum()
    if duplicados > 0: erros.append(f"🚫 {duplicados} linhas duplicadas (Risco de cobrança em dobro).")
    return erros

def salvar_log_uso(duvida, nivel):
    """Grava o uso para o Dashboard da Isa."""
    log_file = "uso_copilot_log.csv"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    novo_log = pd.DataFrame([{"Data": timestamp, "Pergunta": duvida, "Nível": nivel}])
    
    header = not os.path.exists(log_file)
    novo_log.to_csv(log_file, mode='a', index=False, header=header)