import io
import json
import time
import pandas as pd
from connection.connectdb import Connect
from configs.logging_config import logger


class save_from_excel():
        
    def __init__(self, code:int=6816197):
        self.db = Connect()
        sql_empresa = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'getnet' = '{code}'"
        self.empresa = self.db.execute(sql_empresa)[0]

    def get_vendas(self):
        #Tratamento Dataframe Vendas
        db = self.db
        df = pd.read_excel('vendas.xlsx')
        df.drop(df.columns[[2, 4, 5, 8, 9, 10, 12, 13, 16, 18, 20, 21, 22, 23, 24, 25]], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)
        nome = 'Data/Hora \nda Venda'
        df[nome] = pd.to_datetime(df[nome], format="%d/%m/%Y %H:%M:%S")
        df[nome] = df[nome].dt.strftime("%d/%m/%Y %H:%M")

        # colunas = ['cod_empresa', 'NumeroVenda', 'NSU']
        colunas = ['Cód. Estabelecimento', 'Número do Comprovante \nde Vendas', 'Número da Autorização']
        for col in colunas:
            df[col] = df[col].astype(str)

        df.insert((len(df.columns)-1), 'TaxaMdr', None)
        for i, item in enumerate(df['Valor Bruto']):
            valorMdr = df.loc[i, 'Valor Bruto'] - df.loc[i, 'Valor Líquido']
            df.loc[i, 'TaxaMdr'] = round(((valorMdr / df.loc[i, 'Valor Bruto'])*100), 2)

        for i, item in enumerate(df['Valor da Taxa \ne/ou Tarifa']):
            df.loc[i, 'Valor da Taxa \ne/ou Tarifa'] = df.loc[i, 'Valor da Taxa \ne/ou Tarifa']*-1

        df['Empresa'] = self.empresa
        index = ["cod_empresa", "DataVenda", "Valor", "TaxaMdr", "ValorMdr", "ValorLiquido", 
                     "Modalidade", "Parcelas", "NSU", "NumeroVenda", "Cartao", "Empresa"]
        
        new_names = ["cod_empresa", "Cartao", "DataVenda", "NSU", "NumeroVenda", "Modalidade", "Parcelas", 
                 "Valor", "TaxaMdr", "ValorMdr", "ValorLiquido", "Empresa"]
        df = df.set_axis(new_names, axis=1, copy=False)
        df = df.reindex(columns=index)

        json_df = io.StringIO()
        isso = df.to_dict('records')
        json.dump(isso, json_df)

        data = json_df.getvalue()
        data = json.loads(data)
        
        for i, reg in enumerate(data):
            valores = [reg["cod_empresa"],
                    reg['DataVenda'],
                    reg["Valor"],
                    reg["TaxaMdr"],
                    reg["ValorMdr"],
                    reg["ValorLiquido"],
                    reg["Modalidade"],
                    reg["Parcelas"],
                    reg["NSU"],
                    reg["NumeroVenda"],
                    reg["Cartao"],
                    reg['Empresa']]
            try:
                valores[6] = valores[6].replace("VENDA ", "")
                logger.debug(f"linha: {i} - {valores}")
            except:
                logger.error(f"Erro de leitura de valores na linha {i}")
                logger.error(valores)
            db.send_vendas(valores)
        #--------------------------------------------------
    
    def get_receivables(self): 
        db = self.db
        df = pd.read_excel("recebiveis.xlsx", sheet_name="Analitico")
        df.drop(df.columns[[0, 3, 6, 9, 12]], axis=1, inplace=True)
        df.reset_index(drop=True, inplace=True)

        for i, reg in enumerate(df['LANÇAMENTO'].values):
            if not str(reg).__contains__('Venda'):
                df = df.drop(i, axis=0)
                
        df = df.reset_index(drop=True)
        df = df.drop(columns=['LANÇAMENTO'])

        colunas = ['CÓDIGO EC', 'NÚMERO DO CV', 'AUTORIZAÇÃO']
        for col in colunas:
            df[col] = df[col].astype(str)

         # df.insert((len(df.columns)), 'TaxaMdr', None)
        for i, item in enumerate(df['VALOR BRUTO']):
            try:
                valorMdr = item - df.loc[i, 'LIQUIDO']
                df.loc[i, 'TaxaMdr'] = round(((valorMdr / item)*100), 2)
            except KeyError:
                logger.debug(f"{df.iloc[i].tolist()}")
                logger.debug(df.index)

        df['Empresa'] = self.empresa
        index = ["cod_empresa", "DataVenda", "DataRecebimento", "ValorOriginal", "ValorBruto", "ValorLiquido", 
                 "ValorMdr", "TaxaMdr", "Parcela", "TotalParcelas", "NSU", "NumeroVenda", "Modalidade", "Empresa"]
        new_names = ["cod_empresa", "DataRecebimento", "Modalidade", "Parcela", "TotalParcelas", "NSU", 
                     "NumeroVenda", "DataVenda", "ValorOriginal", "ValorBruto", "ValorMdr", "ValorLiquido", "TaxaMdr", "Empresa"]

        
        df = df.set_axis(new_names, axis=1, copy=False)
        df = df.reindex(columns=index)

        for i, item in enumerate(df['ValorMdr']):
            df.loc[i, 'ValorMdr'] = df.loc[i, 'ValorMdr']*-1

        print(df.info())
        print(df.head())

        for i in df.index:
            db.send("recebiveis", df.iloc[i].tolist())

teste = save_from_excel()
# teste.get_vendas()
teste.get_receivables()

