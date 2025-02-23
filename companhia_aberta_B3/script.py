import pandas as pd
import sqlite3

# URL para do arquivo de dados da CVM
csv_file = "https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv"

#Construindo dataframe
df = pd.read_csv(csv_file, delimiter=';', encoding='latin1')

# Conecta ou cria um banco de dados SQLite e salva os dados
db_name = 'companhias_abertas.db'
conn = sqlite3.connect(db_name)
df.to_sql('companhias_abertas', conn, if_exists='replace', index=False)
conn.close()