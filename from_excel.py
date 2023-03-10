import io
import json
import traceback
from configs.logging_config import logger
import time
import pandas as pd
from connection.connectdb import Connect

db = Connect()
con = db.con
cur = db.cursor

# #Tratamento Dataframe Vendas
# df = pd.read_excel('vendas2.xlsx')
# df['DataVenda'] = pd.to_datetime(df['DataVenda'], format='%d/%m/%Y %H:%M:%S')
# df['DataVenda'] = df['DataVenda'].dt.strftime("%d/%m/%Y %H:%M")

# colunas = ['cod_empresa', 'NumeroVenda', 'NSU']
# for col in colunas:
#     df[col] = df[col].astype(str)

# df.insert((len(df.columns)-1), 'TaxaMdr', None)
# for i, item in enumerate(df['Valor']):
#     valorMdr = df.loc[i, 'Valor'] - df.loc[i, 'ValorLiquido']
#     df.loc[i, 'TaxaMdr'] = round(((valorMdr / df.loc[i, 'Valor'])*100), 2)

# for i, item in enumerate(df['ValorMdr']):
#     df.loc[i, 'ValorMdr'] = df.loc[i, 'ValorMdr']*-1

# empresa = sql_empresa = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'getnet' = '{6816197}'"
# empresa = db.get_db(sql_empresa).loc[0, 'name']

# df['Empresa'] = empresa

# json_df = io.StringIO()
# isso = df.to_dict('records')
# json.dump(isso, json_df)

# data = json_df.getvalue()
# data = json.loads(data)

# for reg in data:
#     valores = [reg["cod_empresa"],
#             reg['DataVenda'],
#             reg["Valor"],
#             reg["TaxaMdr"],
#             reg["ValorMdr"],
#             reg["ValorLiquido"],
#             reg["Modalidade"],
#             reg["Parcelas"],
#             reg["NSU"],
#             reg["NumeroVenda"],
#             reg["Cartao"],
#             reg['Empresa']]
#     valores[6] = valores[6].replace("VENDA ", "")
#     print(valores)
#     db.send_vendas(valores)
#--------------------------------------------------
df = pd.read_excel("recebiveis.xlsx")

print(df.head())
print(df.info())

for i, reg in enumerate(df['LANÇAMENTO'].values):
    if not str(reg).__contains__('Venda'):
        df = df.drop(i, axis=0)
        
df = df.reset_index(drop=True)
df = df.drop(columns=['LANÇAMENTO'])

colunas = ['cod_empresa', 'NumeroVenda', 'NSU']
for col in colunas:
    df[col] = df[col].astype(str)

# df.insert((len(df.columns)), 'TaxaMdr', None)
for i, item in enumerate(df['ValorBruto']):
    
    try:
        valorMdr = item - df.loc[i, 'Liquido']
        df.loc[i, 'TaxaMdr'] = round(((valorMdr / item)*100), 2)
    except KeyError:
        logger.debug(f"{df.iloc[i].tolist()}")
        logger.debug(df.index)



for i, item in enumerate(df['ValorMdr']):
    df.loc[i, 'ValorMdr'] = df.loc[i, 'ValorMdr']*-1

empresa = sql_empresa = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'getnet' = '{6816197}'"
empresa = db.get_db(sql_empresa).loc[0, 'name']

df['Empresa'] = empresa

df = df.reindex(columns=['cod_empresa', 'DataVenda', 'DataRecebimento',  'ValorOriginal', 'ValorBruto',
                         'Liquido', 'TaxaMdr', 'ValorMdr', 'Parcela', 'TotalParcelas', 'NSU', 'NumeroVenda', 'Modalidade', 'Empresa'])

print(df.info())
print(df.head())

for i in df.index:
    db.send("recebiveis", df.iloc[i].tolist())


