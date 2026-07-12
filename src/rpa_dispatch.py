import logging
import pyautogui
import time
import datetime
import os
from fpdf import FPDF

# 1. Garante que a pasta de logs existe
os.makedirs("logs", exist_ok=True)

# 2. Configuração forçada de Log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("logs/pyra_system.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True # O force=True é essencial aqui para o Streamlit não bloquear a gravação
)

# Kill Switch ativo
pyautogui.FAILSAFE = False 
pyautogui.PAUSE = 0.5

def pausa_segura(segundos: float) -> None:
    """Monitorização ativa do mouse. Jogue para o canto superior direito para abortar."""
    largura, altura = pyautogui.size()
    tempo_final = time.time() + segundos
    
    while time.time() < tempo_final:
        x, y = pyautogui.position()
        if x >= largura - 5 and y <= 5:
            raise Exception("KILL SWITCH ACIONADO: Aborto de emergência do RPA.")
        time.sleep(0.1)

def gerar_relatorio_tecnico(id_alerta: str, satelite: str, lat: float, lon: float, confianca: float) -> str:
    """Gera o relatório PDF em background enquanto o terminal roda visualmente."""
    logging.info("Gerando relatório técnico em PDF...")
    output_dir = os.path.join("data", "relatorios_gerados")
    os.makedirs(output_dir, exist_ok=True)
    caminho_pdf = os.path.join(output_dir, f"Relatorio_{id_alerta}.pdf")
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Courier", 'B', 16)
    pdf.cell(200, 10, txt="PYRA - RELATÓRIO OFICIAL DE INCIDENTE", ln=True, align='C')
    pdf.set_font("Courier", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"DATA/HORA DO DISPARO : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt=f"ID DO ALERTA         : {id_alerta}", ln=True)
    pdf.cell(200, 10, txt=f"FONTE DE TELEMETRIA  : {satelite}", ln=True)
    pdf.cell(200, 10, txt=f"COORDENADAS DE ALVO  : LAT {lat} | LON {lon}", ln=True)
    pdf.cell(200, 10, txt=f"CONFIANÇA PREDITIVA  : {confianca}%", ln=True)
    pdf.cell(200, 10, txt="STATUS DA ORDEM      : DESPACHO AUTORIZADO POR OPERADOR RPA", ln=True)
    
    pdf.output(caminho_pdf)
    logging.info(f"Arquivo salvo: {caminho_pdf}")
    return caminho_pdf

def despachar_equipe_erp(dados_alerta: dict) -> None:
    """Executa a interface de linha de comandos via orquestração de Batch Script."""
    logging.info("INICIANDO SEQUÊNCIA DE TERMINAL (Não toque no teclado...)")
    
    # 1. Criação Dinâmica do Script na pasta 'data' para evitar exclusão prematura
    diretorio_script = os.path.abspath("data")
    os.makedirs(diretorio_script, exist_ok=True)
    caminho_script = os.path.join(diretorio_script, "pyra_boot.bat")
    
    # Script rodando no CMD
    conteudo_bat = f"""@echo off
color 0A
cls
echo ==========================================================
echo      [ P Y R A  -  O R B I T A L  D I S P A T C H ]       
echo ==========================================================
echo.
echo [SYSTEM] Inicializando modulos de telemetria...
timeout /t 1 >nul
echo [SYSTEM] Bypass de seguranca concluido com sucesso.
timeout /t 1 >nul
echo [SYSTEM] Autenticando credenciais do operador Streamlit...
timeout /t 1 >nul
echo [SYSTEM] Acesso Garantido. Conectando uplink com equipe...
timeout /t 1 >nul
echo.
echo [COMANDO] INJETANDO COORDENADAS -- LAT: {dados_alerta['lat']} -- LON: {dados_alerta['lon']}
timeout /t 2 >nul
echo.
echo [SYSTEM] Sincronizando ERP de missao:
echo [##                  ] 10%%
timeout /t 1 >nul
echo [######              ] 30%%
timeout /t 1 >nul
echo [############        ] 60%%
timeout /t 1 >nul
echo [##################  ] 90%%
timeout /t 1 >nul
echo [####################] 100%% - SINCRONIZADO
echo.
timeout /t 1 >nul
echo [SUCESSO] Ordem de despacho confirmada. Gerando PDF...
timeout /t 2 >nul
exit
"""
    # Salva o arquivo temporário
    with open(caminho_script, "w", encoding="utf-8") as f:
        f.write(conteudo_bat)

    pausa_segura(1) 
    
    try:
        # 2. Abertura do Terminal
        pyautogui.press('win')
        pausa_segura(0.5)
        pyautogui.write('cmd')
        pausa_segura(0.5)
        pyautogui.press('enter')
        pausa_segura(1.5)
        
        pyautogui.hotkey('win', 'up') # Maximiza a janela
        pausa_segura(1)
        
        # 3. O RPA digita o caminho absoluto do script entre aspas (para evitar erros com espaços)
        pyautogui.write(f'"{caminho_script}"', interval=0.01)
        pyautogui.press('enter')
        
        # Aguarda o tempo do show visual (10 segundos)
        pausa_segura(10)
        
        # 4. Gera o PDF estruturado em background
        gerar_relatorio_tecnico(
            id_alerta=dados_alerta.get('id', 'N/A'),
            satelite="MODIS-ORBITAL",
            lat=dados_alerta.get('lat', 0),
            lon=dados_alerta.get('lon', 0),
            confianca=98.4
        )
        
        logging.info("Sequência CLI finalizada com sucesso.")
        
    except Exception as e:
        logging.error(f"OPERAÇÃO RPA ABORTADA: {e}")
        raise