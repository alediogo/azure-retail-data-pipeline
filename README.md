<div align="center">

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![MicrosoftSQLServer](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft%20sql%20server&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![Data Engineering](https://img.shields.io/badge/Data%20Engineering-Pipeline-orange?style=for-the-badge)

</div>

# 🛒 Azure Retail Data Pipeline

Pipeline de Engenharia de Dados ETL (Extract, Transform, Load) que simula um ambiente de varejo, gerando dados transacionais e carregando-os em um Data Warehouse na nuvem (Azure SQL Database).

## ⚙️ Arquitetura da Solução

## 📋 Sobre o Projeto

Abaixo, o fluxo de dados desde a extração local até o carregamento no Azure:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#007ACC', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f4f4f4'}}}%%
graph LR
    subgraph Local_Env ["💻 Ambiente Local (Dev Machine)"]
        style Local_Env fill:#f9f9f9,stroke:#333,stroke-width:2px
        direction TB
        
        Python[("🐍 Script Python ETL<br/>(Pandas + PyODBC)")]
        style Python fill:#FFD43B,stroke:#333,color:black
        
        Env[("🔒 Arquivo .env<br/>(Credenciais Seguras)")]
        style Env fill:#ffcccc,stroke:red,stroke-dasharray: 5 5
        
        Logs["📄 Logs de Execução<br/>(Auditoria & Monitoramento)"]
        style Logs fill:#e1e1e1,stroke:#333
        
        Env -.->|"Lê Senhas"| Python
        Python -->|"Grava Histórico"| Logs
    end

    %% O Fluxo Principal %%
    Python ===>|"🚀 Processo ETL<br/>(Internet Segura)"| AzureDB

    subgraph Azure_Cloud ["☁️ Microsoft Azure Cloud"]
        style Azure_Cloud fill:#cceeff,stroke:#007ACC,stroke-width:2px
        direction TB
        
        AzureDB[("🛢️ Azure SQL Database<br/>(Serverless Tier)")]
        style AzureDB fill:#007ACC,stroke:#fff,color:white

        subgraph Star_Schema ["⭐ Modelagem Star Schema (DW)"]
            style Star_Schema fill:#e6f7ff,stroke:#007ACC,stroke-dasharray: 5 5
            direction TB
            
            %% --- TRUQUE DE ESPAÇAMENTO ---
            Spacer[ ] 
            style Spacer fill:none,stroke:none,height:0px
            %% -----------------------------

            Fato("⬜ Tabela FatoVendas<br/>(Transações & Métricas)")
            style Fato fill:#fff,stroke:#333,stroke-width:2px
            
            Dim("⬜ Tabela DimProduto<br/>(Catálogo & Detalhes)")
            style Dim fill:#fff,stroke:#333

            %% Conecta o Spacer na Fato para empurrar ela pra baixo, mas esconde a linha
            Spacer --- Fato 
            linkStyle 3 stroke-width:0px
            
            Fato -->|"FK (1:N)"| Dim
        end

        AzureDB --- Star_Schema
    end
```

Este projeto demonstra a criação de uma infraestrutura de dados moderna e segura. O script Python atua como um orquestrador que gera dados de vendas realistas (com regras de negócio), aplica modelagem dimensional (Star Schema) e carrega os dados no Azure.

### 🛠 Tecnologias Utilizadas
* **Linguagem:** Python 3.12
* **Cloud:** Microsoft Azure SQL Database (Serverless)
* **Bibliotecas:** Pandas (Transformação), PyODBC (Conector SQL), Python-Dotenv (Segurança), Logging (Observabilidade).
* **Modelagem:** Star Schema (Fato e Dimensão).

### ⭐ Modelagem de Dados (Star Schema)
Os dados foram modelados seguindo as melhores práticas de Data Warehousing (Kimball), separando Fatos (métricas) de Dimensões (contexto):

```mermaid
erDiagram
    %% Relação: Um produto pode estar em muitas vendas (1 para N)
    DimProduto ||--o{ FatoVendas : "É vendido em"

    DimProduto {
        int ID_Produto PK "Chave Primária"
        varchar Nome
        varchar Categoria
        decimal PrecoBase
    }

    FatoVendas {
        int ID_Venda PK "Chave Primária"
        int ID_Produto FK "Chave Estrangeira"
        datetime DataVenda
        int Quantidade
        decimal ValorTotal
        varchar EmailCliente "Enriquecimento"
        varchar CanalVenda "Enriquecimento"
        varchar StatusVenda "Enriquecimento"
    }
```

## ⚙️ Arquitetura e Funcionalidades

1.  **Segurança de Credenciais:** Uso de variáveis de ambiente (`.env`) para não expor senhas no código.
2.  **Modelagem Star Schema:**
    * `DimProduto`: Tabela dimensão com catálogo de produtos.
    * `FatoVendas`: Tabela fato com transações, chaves estrangeiras e métricas.
3.  **Enriquecimento de Dados:**
    * Simulação de **Canais de Venda** (App, Site, Loja Física).
    * Status do pedido (Aprovado, Cancelado, Pendente).
    * Geração de e-mails de clientes para CRM.
4.  **Logging e Monitoramento:** Geração automática de arquivos de log (`pipeline_vendas.log`) registrando cada etapa do processo ETL.

## 🚀 Como Executar

1.  Clone o repositório.
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3.  Crie um arquivo `.env` na raiz com suas credenciais do Azure:
    ```env
    AZURE_SERVER=seu-servidor.database.windows.net
    AZURE_DB=SeuBanco
    AZURE_USER=SeuUsuario
    AZURE_PWD=SuaSenha
    ```
4.  Execute o pipeline:
    ```bash
    python etl_completo_final.py
    ```

## 📊 Exemplo de Consulta (SQL)

Após a execução, é possível analisar os dados no Azure:

```sql
SELECT TOP 20
    P.Nome AS Produto,
    P.Categoria,
	P.ID_Produto,
    P.Categoria,
    P.PrecoBase,
    V.ID_Venda,
    V.ID_Produto,
    V.DataVenda,
    V.Quantidade,
    V.ValorTotal
FROM [dbo].[FatoVendas] V
JOIN [dbo].[DimProduto] P ON V.ID_Produto = P.ID_Produto
ORDER BY V.DataVenda DESC;

```

## 📊 Resultado da Consulta
![Resultado SQL](img/resultado_query.png)
