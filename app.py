import streamlit as st
import pandas as pd
import pickle
import os
import time
import logging
from src import rpa_dispatch
import sys

# Fix encoding Windows — garante UTF-8 no console (cmd.exe / PowerShell)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Configuração da Página 
st.set_page_config(
    page_title="PYRA - Controle de Incidentes", 
    page_icon="🛰️", 
    layout="wide"
)

# Funções de Carregamento de Dados e Recursos 
@st.cache_resource
def carregar_modelo():
    """Carrega o Motor de IA preditivo"""
    caminho = os.path.join("models", "motor_pyra.pkl")
    if os.path.exists(caminho):
        with open(caminho, 'rb') as f:
            return pickle.load(f)
    return None

def carregar_telemetria():
    """Carrega os dados extraídos da NASA"""
    caminho = os.path.join("data/relatorios_gerados", "base_telemetria_orbital.csv")
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return None

def ler_logs():
    """Lê o log para exibir no terminal da UI"""
    caminho = os.path.join("logs", "pyra_system.log")
    if os.path.exists(caminho):
        with open(caminho, "r", encoding="utf-8", errors="replace") as f:
            return f.readlines()
    return ["Nenhum log de sistema encontrado ainda."]

# Sidebar - Filtros, Status e Auditoria 
st.sidebar.title("🛰️ PYRA Central")
st.sidebar.markdown("---")

df_telemetria = carregar_telemetria()
modelo_ia = carregar_modelo()

if df_telemetria is not None:
    st.sidebar.subheader("🎛️ Filtros de Bioma")
    
    # Filtro Dinâmico por Macro-regiões (Agrupadas no Scraper)
    lista_biomas = df_telemetria['bioma_alvo'].unique().tolist()
    bioma_selecionado = st.sidebar.selectbox("Filtrar por Setor (Bioma):", ["Todos"] + lista_biomas)
    
    st.sidebar.markdown("---")
    
    # Indicadores de Status em Tempo Real
    st.sidebar.subheader("🖥️ Status")
    st.sidebar.success(f"Satélites Ativos: {df_telemetria['id_satelite'].nunique()}")
    st.sidebar.warning(f"Anomalias na Fila: {len(df_telemetria)}")
    
    st.sidebar.markdown("---")
    
    # Download do Log para Auditoria
    st.sidebar.subheader("📄 Auditoria RPA")
    log_file_path = os.path.join("logs", "pyra_system.log")
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8", errors="replace") as log_file:
            st.sidebar.download_button(
                label="📥 Baixar Log do Sistema (.txt)",
                data=log_file,
                file_name="pyra_auditoria.txt",
                mime="text/plain",
                use_container_width=True
            )

# Parte principal do Painel - Exibição de Dados, Métricas e Ações
st.title("Painel de Gestão de Anomalias Térmicas")
st.markdown("Integração de IA para Automação de Despacho (AI for RPA)")

if df_telemetria is not None and modelo_ia is not None:
    
    # Aplicação do Filtro da Sidebar no DataFrame Principal
    if bioma_selecionado != "Todos":
        df_exibicao = df_telemetria[df_telemetria['bioma_alvo'] == bioma_selecionado]
    else:
        df_exibicao = df_telemetria
        
    st.subheader("📡 Telemetria Orbital Recente (100 Focos Críticos)")
    st.dataframe(df_exibicao, use_container_width=True)
    st.markdown("---")
    
    if not df_exibicao.empty:
        st.subheader("⚠️ Inspeção e Validação de Alertas")
        
        # Criação de rótulos explícitos e legíveis para cada linha capturada
        opcoes_alvo = df_exibicao.apply(
            lambda row: f"🔥 {row['brilho_temp_k']}K | 🛰️ {row['id_satelite']} | 📍 {row['bioma_alvo']} (Lat {row['lat']})", 
            axis=1
        ).tolist()
        
        # Dropdown interativo para a seleção ativa do operador humano
        alvo_selecionado = st.selectbox(
            "Selecione o foco crítico para análise detalhada e despacho:",
            opcoes_alvo
        )
        
        # Mapeamento do item selecionado de volta para os dados da linha
        indice_selecionado = opcoes_alvo.index(alvo_selecionado)
        alerta_atual = df_exibicao.iloc[indice_selecionado]
        
        # Motor de IA entrando em ação
        # Criam um DataFrame na hora com a temperatura real da NASA e um índice de aridez simulado do bioma
        input_ia = pd.DataFrame({
            'brilho_temp_k': [alerta_atual['brilho_temp_k']],
            'indice_aridez': [0.75] # Fator de seca do terreno (0 a 1)
        })
        
        # O modelo prevê a probabilidade de ser um incêndio crítico (Classe 1)
        probabilidade_ia = modelo_ia.predict_proba(input_ia)[0][1] * 100
        
        # Atualização Dinâmica dos Cartões de Métricas
        col1, col2, col3 = st.columns(3)
        col1.metric("Satélite / Sensor", alerta_atual['id_satelite'])
        col2.metric("Temperatura Brilho (K)", f"{alerta_atual['brilho_temp_k']} K", "- Crítico")
        
        # A tela mostra a matemática real do Random Forest
        col3.metric("Confiança da IA (Random Forest)", f"{probabilidade_ia:.1f}%", "Ação Recomendada")
            
        st.warning(f"**IA:** Risco estrutural detectado na região **{alerta_atual['bioma_alvo']}** (Coord: {alerta_atual['lat']}, {alerta_atual['lon']}). Aguardando validação humana.")
        
        st.markdown("### Ação do Operador")
        if st.button("🚨 APROVAR ALERTA E ENGATILHAR RPA DO EXCEL", type="primary"):
            with st.spinner("Automação assumindo o controle. Por favor, não mova o mouse..."):
                
                # Payload único enviado para a automação
                payload = {
                    "id": f"PYRA-{int(time.time())}", 
                    "lat": alerta_atual['lat'],
                    "lon": alerta_atual['lon']
                }
                
                # Executa o disparo do robô visual
                rpa_dispatch.despachar_equipe_erp(payload)
                
                # Registra a ação do utilizador diretamente no log do sistema
                logger = logging.getLogger("PYRA_UI")
                logger.info(f"Operador validou despacho para alerta {payload['id']} na região {alerta_atual['bioma_alvo']}")
                
            st.success(f"✅ Fluxo finalizado! Equipe despachada para {alerta_atual['bioma_alvo']} e planilha gerada com sucesso.")
            st.balloons()
            
    # Terminal de logs do sistema para monitoramento em tempo real
    st.markdown("---")
    with st.expander("💻 Terminal de Logs do Sistema (Backend)"):
        logs_sistema = ler_logs()
        # Exibe as últimas 15 entradas ordenadas com as mais recentes no topo
        texto_log = "".join(logs_sistema[-15:][::-1])
        st.code(texto_log, language="bash")
        
else:
    st.error("⚠️ Base de dados ou Modelo IA ausente.")
    st.info("Execute 'python src/ml_pipeline.py' e 'python src/scraper_inpe.py' no terminal antes de inicializar o painel.")