import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Garante que a pasta de logs existe
os.makedirs("logs", exist_ok=True)

# Salva no arquivo e mostra no terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler("logs/pyra_system.log"),
        logging.StreamHandler()
    ]
)

def treinar_modelo_pyra() -> None:
    """Gera dados sintéticos, treina o classificador de risco e exporta o modelo .pkl."""
    logging.info("Iniciando treinamento do Motor de Fusão Preditivo...")

    np.random.seed(42)
    qtd_amostras = 1000

    dados = {
        'brilho_temp_k': np.random.normal(320, 20, qtd_amostras),
        'indice_aridez': np.random.uniform(0.1, 0.9, qtd_amostras)
    }
    df = pd.DataFrame(dados)
    df['risco_critico'] = np.where((df['brilho_temp_k'] > 340) & (df['indice_aridez'] > 0.6), 1, 0)

    X = df.drop('risco_critico', axis=1)
    y = df['risco_critico']

    logging.info("Treinando classificador Random Forest...")
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X, y)

    output_dir = "models"
    os.makedirs(output_dir, exist_ok=True)
    caminho_pkl = os.path.join(output_dir, "motor_pyra.pkl")

    with open(caminho_pkl, 'wb') as arquivo:
        pickle.dump(modelo, arquivo)

    logging.info(f"Pipeline salvo com sucesso em: {caminho_pkl}")

if __name__ == "__main__":
    treinar_modelo_pyra()