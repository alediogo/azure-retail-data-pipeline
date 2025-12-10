import pyodbc
import pandas as pd
import random
import os
import logging 
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. Configuração do LOG (Com correção de acentos UTF-8)
logging.basicConfig(
    filename='pipeline_vendas.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8' 
)

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- CONFIGURAÇÕES SEGURAS ---
server = os.getenv('AZURE_SERVER')
database = os.getenv('AZURE_DB')
username = os.getenv('AZURE_USER')
password = os.getenv('AZURE_PWD')
driver = '{ODBC Driver 17 for SQL Server}'

logging.info("--- INICIANDO PROCESSO DE ETL ---")

def get_db_connection():
    try:
        connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
        return pyodbc.connect(connection_string)
    except Exception as e:
        logging.error(f"Falha ao conectar no Azure: {e}")
        raise e

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    logging.info("Conexão com Azure SQL estabelecida com sucesso.")

    # ---------------------------------------------------------
    # ETAPA 1: INFRAESTRUTURA
    # ---------------------------------------------------------
    # Vamos manter a recriação das tabelas para garantir o teste limpo
    cursor.execute("DROP TABLE IF EXISTS FatoVendas")
    cursor.execute("DROP TABLE IF EXISTS DimProduto")
    
    # Criar Dimensão
    cursor.execute("""
        CREATE TABLE DimProduto (
            ID_Produto int IDENTITY(1,1) PRIMARY KEY,
            Nome VARCHAR(100) NOT NULL,
            Categoria VARCHAR(50),
            PrecoBase DECIMAL(10, 2)
        )
    """)
    
    # Criar Fato
    cursor.execute("""
        CREATE TABLE FatoVendas (
            ID_Venda int IDENTITY(1,1) PRIMARY KEY,
            ID_Produto int FOREIGN KEY REFERENCES DimProduto(ID_Produto),
            DataVenda DATETIME,
            Quantidade int,
            ValorTotal DECIMAL(10, 2)
        )
    """)
    conn.commit()
    logging.info("Tabelas (Fato e Dimensão) recriadas com sucesso.")

    # ---------------------------------------------------------
    # ETAPA 2: CARREGAR DIMENSÃO
    # ---------------------------------------------------------
    produtos_master = [
        {'Nome': 'Notebook Dell', 'Categoria': 'Eletrônicos', 'Preco': 4500.00},
        {'Nome': 'Mouse Logitech', 'Categoria': 'Periféricos', 'Preco': 150.00},
        {'Nome': 'Monitor LG 24', 'Categoria': 'Monitores', 'Preco': 800.00},
        {'Nome': 'Teclado Mecânico', 'Categoria': 'Periféricos', 'Preco': 350.00},
        {'Nome': 'Cadeira Gamer', 'Categoria': 'Móveis', 'Preco': 1200.00}
    ]

    for prod in produtos_master:
        cursor.execute("INSERT INTO DimProduto (Nome, Categoria, PrecoBase) VALUES (?, ?, ?)", 
                       (prod['Nome'], prod['Categoria'], prod['Preco']))
    conn.commit()
    logging.info(f"Catálogo de produtos carregado: {len(produtos_master)} itens.")

    # Recuperar IDs
    mapa_produtos = {}
    cursor.execute("SELECT Nome, ID_Produto, PrecoBase FROM DimProduto")
    for row in cursor.fetchall():
        mapa_produtos[row[0]] = {'ID': row[1], 'Preco': float(row[2])}

    # ---------------------------------------------------------
    # ETAPA 3: CARREGAR FATO (VENDAS)
    # ---------------------------------------------------------
    qtd_vendas_gerar = 100
    vendas_buffer = []
    
    for _ in range(qtd_vendas_gerar):
        nome_escolhido = random.choice(list(mapa_produtos.keys()))
        dados_prod = mapa_produtos[nome_escolhido]
        
        id_produto_fk = dados_prod['ID']
        preco_base = dados_prod['Preco']
        
        qtd = random.randint(1, 5)
        total = round(qtd * preco_base, 2)
        data = datetime.now() - timedelta(days=random.randint(0, 60))
        
        vendas_buffer.append((id_produto_fk, data, qtd, total))

    cursor.executemany("INSERT INTO FatoVendas (ID_Produto, DataVenda, Quantidade, ValorTotal) VALUES (?, ?, ?, ?)", vendas_buffer)
    conn.commit()
    
    logging.info(f"Carga de Vendas finalizada. {qtd_vendas_gerar} registros inseridos.")
    
    conn.close()
    print("Processo finalizado! Confira o arquivo 'pipeline_vendas.log' na pasta.")

except Exception as e:
    logging.error(f"Erro fatal no processo: {e}")
    print("Ocorreu um erro. Verifique o log.")