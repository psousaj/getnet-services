import io
import json
import pandas as pd
from connection.connectdb import Connect

db = Connect()
con = db.con
cur = db.cursor

#Tratamento Dataframe Vendas
df = pd.read_excel('vendas2.xlsx')
df['DataVenda'] = pd.to_datetime(df['DataVenda'], format='%d/%m/%Y %H:%M:%S')
df['DataVenda'] = df['DataVenda'].dt.strftime("%Y-%m-%d")

colunas = ['cod_empresa', 'NumeroVenda', 'NSU']
for col in colunas:
    df[col] = df[col].astype(str)

df.insert((len(df.columns)-1), 'TaxaMdr', None)
for i, item in enumerate(df['Valor']):
    valorMdr = df.loc[i, 'Valor'] - df.loc[i, 'ValorLiquido']
    df.loc[i, 'TaxaMdr'] = (valorMdr / df.loc[i, 'Valor'])*100

for i, item in enumerate(df['ValorMdr']):
    df.loc[i, 'ValorMdr'] = df.loc[i, 'ValorMdr']*-1

empresa = sql_empresa = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'getnet' = '{6816197}'"
empresa = db.get_db(sql_empresa).loc[0, 'name']

df['Empresa'] = empresa

print(df['Valor'].sum())

json_df = io.StringIO()
isso = df.to_dict('index')

json.dump(isso, json_df)

data = json_df.getvalue()
data = json.loads(data)

for i, dados in enumerate(data):
    valores = [data[f"{i}"]["cod_empresa"],
           data[f"{i}"]["DataVenda"],
           data[f"{i}"]["Valor"],
           data[f"{i}"]["TaxaMdr"],
           data[f"{i}"]["ValorMdr"],
           data[f"{i}"]["ValorLiquido"],
           data[f"{i}"]["Modalidade"],
           data[f"{i}"]["Parcelas"],
           data[f"{i}"]["NSU"],
           data[f"{i}"]["NumeroVenda"],
           data[f"{i}"]["Cartao"],
           data[f"{i}"]['Empresa']]
    valores[6] = valores[6].replace("VENDA ", "")
    db.send_vendas(valores)
