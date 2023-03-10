import io
import json
import datetime
import pandas as pd
from configs.validations import save_excel
from configs.validations import *
from connection.connectdb import Connect
from configs.logging_config import logger

class SumarioVendas:

    def __init__(self, code:int, date:datetime.datetime):
        self.date = date
        self.code = code
        self.open_path = getPath(code, date, "json", complete=True)
        self.lista = []
        self.lista_excel = []
        self.DB = Connect()

    def perform(self):
        """Itera pelo DataFrame e gera as colunas tanto para o banco de dados,
       quanto para gerar a planilha 
        """
        lista = []
        lista_excel = []
        data = load_json(self.open_path)
        for transaction in data['content']['transactions']:
            date = transaction.get('saleDate', None)
            db_values = {
                'cod_empresa': self.code,
                'DataVenda': date,
                'Valor': transaction['amount'],
                'TaxaMdr': transaction['mdrFee'],
                'ValorMdr': transaction['mdrAmount'],
                'ValorLiquido': transaction['netAmount'],
                'Modalidade': transaction['modality']['type'],
                'Parcelas': transaction['installmentQuantity'],
                'NSU': transaction['nsu'],
                'NumeroVenda': transaction['saleSummaryNumber'],
                'Empresa': '',#Pegar no BD
            }
            info = {
                'Empresa': transaction['merchant']['companyName'],
                'Data da Venda': date,
                'Modalidade': f"{transaction['modality']['type']}O {transaction['installmentQuantity']}x",
                'Valor Bruto': transaction['amount'],
                'Valor Líquido': transaction['netAmount'],
                'Soma Venda Bruto': None
            }
            lista.append(db_values)
            lista_excel.append(info)

        self.lista = lista
        self.lista_excel = lista_excel
        return self

    def export(self):
        """Exporta a lista de dados filtrada para o banco de dados e também 
        para uma planilha (O caminho é especificado). Salva também uma cópia na área de trabalho
        """
        desktop = find_desktop_path()
        json_df = io.StringIO()
        json_db = io.StringIO()
        json.dump(self.lista_excel, json_df)
        json.dump(self.lista, json_db)

        logger.info("Mandando para DataBase")
        self.DB.send(json_db.getvalue())

        path = getPath(self.code, self.date, "xlsx", complete=False) #peguei a tupla
        path = format_export(path)

        df = pd.read_json(json_df.getvalue(), orient="columns")
        df = df.sort_values(by='Data da Venda')
        df.loc[0, 'Soma Venda Bruto'] = df['Valor Bruto'].sum()

        save_excel(df, path, desktop)

        logger.debug("---" * 20)
        logger.info(f"Relatório de vendas salvo com sucesso em:\n{path}")


    

