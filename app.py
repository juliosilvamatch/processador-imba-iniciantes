import streamlit as st
import pandas as pd
import numpy as np
import re
import io

# Configuração da Página
st.set_page_config(page_title="Processador Natura & Avon", page_icon="🚀", layout="centered")

# Estilização Customizada
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #2563eb; color: white; }
    .stDownloadButton>button { width: 100%; border-radius: 8px; background-color: #10b981; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# CLASSE DE PROCESSAMENTO
# ==============================================================================
class ProcessadorPlanilhas:
    def __init__(self, ciclo, ano):
        self.ciclo = ciclo
        self.ano = ano
        self.nm_ciclo = f"{ano}{ciclo}"

    def _limpar_dados(self, df):
        df_limpo = df.copy()
        for coluna in df_limpo.columns:
            df_limpo[coluna] = df_limpo[coluna].astype(str).replace({
                'nan': '', 'None': '', 'NaN': '', 'NaT': '', '<NA>': '', 'NULL': '', 'null': ''
            })
            df_limpo[coluna] = df_limpo[coluna].apply(lambda x: x.replace('.0', '') if re.match(r'^\d+\.0$', x) else x)
        return df_limpo

    def _validar_colunas(self, df, colunas_esperadas):
        for col in colunas_esperadas:
            if col not in df.columns: df[col] = ""
        return df[colunas_esperadas]

    def processar_geral(self, df):
        df_final = df.copy()
        col_no = next((c for c in df_final.columns if c.strip().upper() == 'NO'), None)
        if col_no: df_final.rename(columns={col_no: 'NO'}, inplace=True)
        df_final['NM_CICLO'] = self.nm_ciclo
        cols = ['NO', 'NM_CICLO', 'Avon_Topo_Pontos', 'Avon_Topo_Desconto', 'Avon_Base_Valor', 'Avon_Base_Valor_Centavos', 'Avon_Ganhe', 'Avon_Ganhe_Mecanica', 'Natura_Topo_Pontos', 'Natura_Topo_Desconto', 'Natura_Base_Valor', 'Natura_Base_Valor_Centavo', 'Natura_Ganhe', 'Natura_Ganhe_Mecanica', 'Avon_Link_Cta', 'Natura_Link_Cta']
        return self._limpar_dados(self._validar_colunas(df_final, cols))

# ==============================================================================
# INTERFACE STREAMLIT
# ==============================================================================

st.title("🚀 Processador Imbatíveis Iniciantes")
st.subheader("Natura & Avon")

with st.expander("1. Configurações do Ciclo", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        ano = st.number_input("Ano", min_value=2024, max_value=2030, value=2025)
    with col2:
        ciclo = st.number_input("Ciclo", min_value=1, max_value=20, value=1)

with st.expander("2. Upload de Arquivo", expanded=True):
    uploaded_file = st.file_uploader("Arraste o arquivo Excel (.xlsx) aqui", type=["xlsx"])

if uploaded_file:
    ciclo_str = str(ciclo).zfill(2)
    ano_str = str(ano)
    
    if st.button("Iniciar Processamento"):
        try:
            xl = pd.ExcelFile(uploaded_file)
            processor = ProcessadorPlanilhas(ciclo_str, ano_str)
            
            st.success("Arquivo lido com sucesso! Processando abas...")
            
            # Mapeamento de abas e funções
            abas_config = {
                'Geral': (['Geral'], processor.processar_geral),
                # Adicione aqui as outras funções (Avon, Natura, Cards) conforme sua classe
            }
            
            for chave, (nomes_possiveis, func_proc) in abas_config.items():
                aba_real = None
                for n in nomes_possiveis:
                    if n.lower() in [s.lower() for s in xl.sheet_names]:
                        aba_real = next(s for s in xl.sheet_names if s.lower() == n.lower())
                        break
                
                if aba_real:
                    df_raw = xl.parse(aba_real)
                    df_final = func_proc(df_raw)
                    
                    # Botão de Download
                    csv = df_final.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Baixar CSV: {chave}",
                        data=csv,
                        file_name=f"Nova_Imba_{chave}_C{ciclo_str}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning(f"Aba '{chave}' não encontrada no arquivo.")
                    
        except Exception as e:
            st.error(f"Erro no processamento: {e}")
