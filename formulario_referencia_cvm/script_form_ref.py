import requests
import zipfile
import io
import pandas as pd
import sqlite3

# URL do arquivo ZIP de companhias abertas cvm de 2025
for ano in range(2023, 2026):
    url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_{}.zip".format(ano)

    # Realiza o download do arquivo ZIP
    response = requests.get(url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))

    # Extrai os arquivos necessários e cria DataFrames com eles
    file_names = [
        "fre_cia_aberta_empregado_local_faixa_etaria_{}.csv".format(ano),
        "fre_cia_aberta_empregado_local_declaracao_raca_{}.csv".format(ano),
        "fre_cia_aberta_empregado_local_declaracao_genero_{}.csv".format(ano)
    ]

    dataframes = {}
    for file_name in file_names:
        with zip_file.open(file_name) as file:
            dataframes[file_name] = pd.read_csv(file, delimiter=';', encoding='ISO-8859-1')
            
    # Lista com os nomes dos DataFrames
    dataframe_names = list(dataframes.keys())

    # Nome do banco de dados SQLite
    db_name = 'web_scraping_cvm.db'
    conn = sqlite3.connect(db_name)

    # Salva cada DataFrame em uma tabela separada no banco de dados
    for name, df in dataframes.items():
        # Define um nome de tabela baseado no nome do arquivo, removendo o '.csv' e adicionando o ano
        table_name = name.replace('.csv', '')  # Remove a extensão .csv
        df.to_sql(table_name, conn, if_exists='replace', index=True, index_label="id")

    conn.close()