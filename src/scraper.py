import logging
from playwright.sync_api import sync_playwright
import pandas as pd
import os
import datetime
import time

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - SCRAPER: %(message)s',
    handlers=[logging.FileHandler("logs/system.log"), logging.StreamHandler()]
)

def classificar_macro_regiao(lat: float, lon: float) -> str:
    """
    Algoritmo de geolocalização aproximada por Bounding Boxes.
    Converte coordenadas brutas da NASA em macro-regiões compreensíveis para o operador.
    """
    if lat >= -10 and lon <= -50:
        return "🌳 Amazônia (Setor Norte)"
    elif -25 <= lat <= -10 and -55 <= lon <= -45:
        return "🌾 Cerrado (Setor Central)"
    elif -15 <= lat <= -2 and lon >= -45:
        return "🌵 Caatinga (Setor Nordeste)"
    elif -35 <= lat <= -15 and lon >= -45:
        return "🍃 Mata Atlântica (Setor Litoral)"
    elif -22 <= lat <= -16 and -60 <= lon <= -55:
        return "🐊 Pantanal (Setor Oeste)"
    elif lat <= -25 and lon <= -55:
        return "🏕️ Pampa (Setor Sul)"
    else:
        return "🌍 Outras Áreas / Fronteira Internacional"

def extrair_telemetria_real() -> None:
    logging.info("Iniciando pipeline de ingestão de telemetria real (NASA FIRMS)...")
    output_dir = "data/relatorios_gerados"
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            url_mapa = "https://firms.modaps.eosdis.nasa.gov/map/"
            logging.info(f"RPA acessando painel visual: {url_mapa}")
            page.goto(url_mapa, timeout=90000, wait_until="domcontentloaded")
            logging.info("Renderizando camadas de satélite... (Aguarde)")
            time.sleep(8) 
            
            screenshot_path = os.path.join(output_dir, "captura_satelite.png")
            page.screenshot(path=screenshot_path)
            logging.info(f"Evidência visual da operação salva em: {screenshot_path}")
        except Exception as e:
            logging.error(f"Aviso na renderização visual RPA: {e}")
        finally:
            browser.close()

    logging.info("Iniciando extração do banco de dados live (Últimas 24h)...")
    try:
        url_csv = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_South_America_24h.csv"
        df_real = pd.read_csv(url_csv)
        logging.info(f"Conexão com a NASA estabelecida. {len(df_real)} focos brutos detectados hoje.")
        
        df_real = df_real.rename(columns={
            'satellite': 'id_satelite',
            'latitude': 'lat',
            'longitude': 'lon',
            'brightness': 'brilho_temp_k',
            'confidence': 'confianca'
        })
        df_real['id_satelite'] = df_real['id_satelite'].replace({'A': 'AQUA-MODIS', 'T': 'TERRA-MODIS'})
        
        # Aplica a função de geolocalização no lugar dos números brutos
        df_real['bioma_alvo'] = df_real.apply(lambda row: classificar_macro_regiao(row['lat'], row['lon']), axis=1)
        
        df_real['data_extracao'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Filtra os 100 maiores riscos para ter volume no painel
        df_critico = df_real.sort_values(by='brilho_temp_k', ascending=False).head(100)
        df_final = df_critico[['id_satelite', 'lat', 'lon', 'brilho_temp_k', 'confianca', 'bioma_alvo', 'data_extracao']]
        
        csv_path = os.path.join(output_dir, "base_telemetria_orbital.csv")
        df_final.to_csv(csv_path, index=False)
        logging.info(f"SUCESSO")
        logging.info(f"Dados salvos em: {csv_path}")
        
    except Exception as e:
        logging.error(f"Falha crítica ao processar os dados live da NASA: {e}")

if __name__ == "__main__":
    extrair_telemetria_real()