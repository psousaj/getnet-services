from datetime import datetime
import shutil
import pandas as pd
from utils.validate_fee import *
from configs.validations import *
from configs.logging_config import logger
from connection.connectdb import Connect
from configs.validations import save_excel

class RelatorioPeriodo():

    def __init__(self, date:datetime):
        self.DB = Connect()
        # sql = f'SELECT * FROM getnet.vendas WHERE EXTRACT(MONTH FROM "DataVenda") = {date.month}'
        sql = f'SELECT * from getnet.vendas'
        self.df = self.DB.get_db(sql)
        self.empresa = self.df.loc[0, 'Empresa']
        self.date = date
        self.value = 0

    def perform(self):
        """Consulta os valores e gera a soma do período informado
        """
        values = 0
        for i, date in enumerate(self.df['DataVenda']):
            date = date.strftime("%d/%m/%Y") if not date is None else datetime(2023, 1, 1)
            logger.debug("---" * 10)
            string = f'{date} - {self.empresa}'
            logger.info(string)
            value = self.df.iloc[i]['Valor']
            tx_type = self.df.iloc[i]['Modalidade']
            values += value
            logger.info('Adicionando venda {}: R${:,.2f}'.format(tx_type, value))
        self.value = values
        return self

    def show(self):
        date = self.df['DataVenda'].iloc[0]
        logger.debug("---" * 10)
        logger.info(f"Relatório {self.empresa} - {str(date.strftime('%B')).upper()} ")
        string = 'VALOR TOTAL NO PERIODO: R${:,.2f}'.format(self.value)
        logger.info(string)

    def cert_fee(self):
        df = self.df
        desktop = find_desktop_path()
        path = getPath(df.loc[0, 'cod_empresa'], self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="taxas")
        colunas = ["cod_empresa", "DataVenda", "Valor", "TaxaMdr%", "TaxaEsperada%", "ValorMdr", "ValorLiquido", 
                   "Modalidade", "Parcelas", "NSU", "NumeroVenda", "Cartao", "Empresa"]
        error_df = pd.DataFrame(columns=colunas)

        for i, reg in enumerate(df['TaxaMdr']):
            bandeira_normal = df.loc[i, 'Bandeira']
            bandeira = bandeira_normal
            bandeira = bandeira.replace(" CRÉDITO", "")
            bandeira = bandeira.replace(" DÉBITO", "")

            isvalid = validate(reg, bandeira)
            logger.info(f"{reg} {bandeira_normal} - {isvalid}")

            if not isvalid:
                df['DataVenda'] = pd.to_datetime(df['DataVenda'], format="%d/%m/%Y %H:%M")
                df['DataVenda'] = df['DataVenda'].dt.strftime("%d/%m/%Y %H:%M")
                # error_list.append(df.iloc[i].tolist())
                error = df.iloc[i].tolist()

        # for i, item in enumerate(error_list):
                error_df.loc[i, 'cod_empresa'] = error[0]
                error_df.loc[i, 'DataVenda'] = error[1]
                error_df.loc[i, 'Valor'] = error[2]
                error_df.loc[i, 'TaxaMdr%'] = error[3]
                error_df.loc[i, 'TaxaEsperada%'] = expected_fee(reg, bandeira)
                error_df.loc[i, 'ValorMdr'] = error[4]
                error_df.loc[i, 'ValorLiquido'] = error[5]
                error_df.loc[i, 'Modalidade'] = error[6]
                error_df.loc[i, 'Parcelas'] = error[7]
                error_df.loc[i, 'NSU'] = error[8]
                error_df.loc[i, 'NumeroVenda'] = error[9]
                error_df.loc[i, 'Cartao'] = error[10]
                error_df.loc[i, 'Empresa'] = error[11]
        print(error_df.head())

        save_excel(error_df, path, desktop)
        return self

    def loc_sales_receives(self):
        desktop = find_desktop_path()
        path = getPath(self.empresa, self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="recebimentos-vendas")
        db = self.DB
        sql = '''
        SELECT vendas."NSU", vendas."DataVenda", COALESCE(getnet.recebiveis."DataRecebimento") AS "DataRecebimento", "Valor", vendas."TaxaMdr", vendas."ValorMdr", vendas."ValorLiquido", vendas."Modalidade", vendas."Empresa" 
        FROM getnet.vendas
		LEFT JOIN getnet.recebiveis ON vendas."NSU" = recebiveis."NSU"
        WHERE getnet.recebiveis."NSU" IS NOT NULL;
        '''
        df = db.get_db(sql)
        print(df.head())
        print(df.info())
        save_excel(df, path, desktop)

    def loc_sales_without_receives(self):
        desktop = find_desktop_path()
        path = getPath(self.empresa, self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="vendas-sem-recebimentos")
        db = self.DB
        sql = '''
        SELECT vendas."NSU", vendas."DataVenda", COALESCE(getnet.recebiveis."DataRecebimento") AS "DataRecebimento", "Valor", vendas."TaxaMdr", vendas."ValorMdr", vendas."ValorLiquido", vendas."Modalidade", vendas."Empresa" 
        FROM getnet.vendas
		LEFT JOIN getnet.recebiveis ON vendas."NSU" = recebiveis."NSU"
        WHERE getnet.recebiveis."NSU" IS NULL;
        '''
        df = db.get_db(sql)
        print(df.head())
        print(df.info())
        save_excel(df, path, desktop)
# update public.companies set cod_maquinetas = ('{"getnet":"6816197"}') where cnpj = '32868578000150';