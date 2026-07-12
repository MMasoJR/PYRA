# 🛰️ PYRA - Sistema Preditivo e Resposta Antecipada

**Projeto acadêmico desenvolvido para a Global Solution (AI for RPA) - FIAP.**

O PYRA é uma arquitetura de software end-to-end inspirada nos desafios da Nova Exploração Espacial. O sistema atua como um centro de controle autônomo que ingere telemetria orbital em tempo real, utiliza Machine Learning para inferência de risco e orquestra robôs de software (RPA) para o despacho automatizado de equipes de contenção.

---

## Integrantes

- Gabriel Tonelli Avelino dos Santos - RM 564705
- Marcelo Roberto Maso Junior - RM 562163
- Vinícius Adrian Siqueira de Oliveira - RM 564962

---

## 🏗️ Arquitetura e Fases do Projeto

O projeto consolida quatro grandes pilares tecnológicos em um fluxo contínuo:

1. **Ingestão e Web Scraping (`src/scraper.py`):** Utiliza *Playwright* e *Pandas* para conectar-se ao feed ao vivo da NASA (FIRMS), extraindo coordenadas, temperaturas e gerando evidências visuais (captura de tela do satélite). O algoritmo agrupa as coordenadas brutas em macro-regiões (Biomas) para facilitar a governança humana.
2. **Motor de Inteligência Artificial (`src/ml_pipeline.py`):** Um classificador *Random Forest* treinado com *Scikit-Learn* que avalia a temperatura registrada e a aridez do solo para calcular a probabilidade de risco crítico, atuando como o cérebro decisório do sistema.
3. **Governança Humano-no-Loop (`app.py`):** Interface de comando interativa construída em *Streamlit*. Permite ao operador filtrar os dados espaciais da NASA, visualizar a confiança preditiva da IA e aprovar o disparo do RPA.
4. **Atuação Robótica - RPA (`src/rpa_dispatch.py`):** Orquestração de interface de linha de comandos (CLI) via *PyAutoGUI* e *Batch Scripts*. Após a aprovação humana, o robô assume o controle da máquina, injeta as coordenadas no terminal do sistema operacional e gera um relatório consolidado em `.pdf` documentando a operação.

---

## ⚙️ Pré-requisitos e Instalação

Certifique-se de ter o Python 3.9+ instalado. Para instalar as dependências do projeto, execute no terminal:

```bash
pip install -r requirements.txt
```


## 🚀 Como Executar o Projeto (Passo a Passo)

A execução segue o fluxo de vida do dado, desde a extração até o painel visual:

**Passo 1: Ingestão de Dados da NASA**

Abra o terminal na raiz do projeto e execute o robô extrator para baixar a telemetria do dia:
```bash
python src/scraper.py
```
*(Aguarde o robô abrir o navegador, tirar o print do mapa e salvar o arquivo CSV na pasta `data/`)*

**Passo 2: Treinamento do Pipeline**

Em seguida, faça o treinamento da machine learning com os dados obtidos no passo anterior:
```bash
python src/ml_pipeline.py
```

**Passo 3: Iniciar o Mission Control**

Ainda no terminal, inicie a interface do Streamlit:
```bash
streamlit run app.py
```

**Passo 4: Engatilhar o RPA (Despacho)**

1. Na interface web que se abrirá, utilize a barra lateral para filtrar as anomalias por região.
2. Selecione um foco crítico no menu suspenso (dropdown).
3. Clique no botão **"🚨 APROVAR ALERTA E ENGATILHAR RPA"**.
4. **ATENÇÃO: Solte o mouse e o teclado.** O robô maximizará o terminal do sistema, executará a simulação de despacho via script e salvará o relatório PDF na pasta `data/relatorios_gerados`.