from datetime import datetime
import re
import pandas as pd
from utils.validate_fee import *
from configs.validations import *
from configs.logging_config import logger
from connection.connectdb import Connect
from configs.validations import save_excel

class RelatorioPeriodo():

    def __init__(self, code, date:datetime, retro=False):
        self.DB = Connect()
        self.retro = retro
        sql_empresa = f"SELECT name FROM public.companies WHERE cod_maquinetas ->> 'getnet' = '{code}'"
        self.empresa = self.DB.execute(sql_empresa)[0]
        sql = f'SELECT * FROM getnet.vendas WHERE "Empresa" = \'{self.empresa}\'' if retro else f'SELECT * FROM getnet.vendas WHERE to_char("DataVenda", \'YYYY-MM\') = \'{date.year}-{date.strftime("%m")}\' AND "Empresa" = \'{self.empresa}\''
        try: self.df = self.DB.get_db(sql) 
        except Exception: logger.info("Não há registros de vendas referentes ao período desejado"); sys.exit() 
        self.date = date
        self.value = 0
        self.counter = {'fee_errors': 0, 'not_receivables': 0, 'payments':0, 'sales':self.df['NSU'].size}
        self.report_path = get_report_path()
        

    def get_values(self):
        """Consulta os valores e gera a soma do período informado
        """
        values = 0
        for i, date in enumerate(self.df['DataVenda']):
            # date = datetime.datetime.strptime(date, "%d/%m/%Y %H:%M")
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
        date = self.date
        mes = str(date.strftime('%B')).upper() if not self.retro else ''
        logger.debug("---" * 10)
        logger.info(f"RELATÓRIO {self.empresa} - {mes}")
        string = 'Valor total no período: R${:,.2f}'.format(self.value)
        logger.info(string)
        logger.info(f"Total de vendas: {self.counter['sales']}")
        logger.info(f"Recebimentos vendas: {self.counter['payments']}")
        logger.info(f"Erros em taxas: {self.counter['fee_errors']}")
        strf = f"Vendas sem recebimentos: {self.counter['not_receivables']}" if self.counter['not_receivables'] != 0 else "Não há registros referentes à vendas sem recebimentos no período"
        logger.info(strf)
        logger.debug("-"*20)
        logger.info(f"Arquivos salvos em: \n{self.report_path}")

    def cert_fee(self):
        df = self.df
        desktop = find_desktop_path()
        path = getPath(df.loc[0, 'cod_empresa'], self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="taxas", retro=self.retro)
        colunas = ["DataVenda", "Cartao", "Valor", "TaxaMdr%", "TaxaEsperada%", "ValorMdr", "ValorLiquido", 
                   "Modalidade", "Parcelas", "NSU", "NumeroVenda", "Empresa"]
        error_df = pd.DataFrame(columns=colunas)

        for i, fee in enumerate(df['TaxaMdr']):
            bandeira_normal = df.loc[i, 'Bandeira']
            bandeira = bandeira_normal
            bandeira = bandeira.replace(" CRÉDITO", "")
            bandeira = bandeira.replace(" DÉBITO", "")
            chave = re.sub(r'^.*(?=DÉBITO)', '', bandeira_normal)
            chave = re.sub(r'^.*(?=CRÉDITO)', '', bandeira_normal)

            isvalid = validate(fee, bandeira, chave)
            logger.info(f"{fee} {bandeira_normal} - {isvalid}")

            if not isvalid:
                df['DataVenda'] = pd.to_datetime(df['DataVenda'], format="%d/%m/%Y %H:%M")
                df['DataVenda'] = df['DataVenda'].dt.strftime("%d/%m/%Y %H:%M")
                error = df.iloc[i].tolist()
                self.counter['fee_errors'] += 1

                error_df.loc[i, 'DataVenda'] = error[1]
                error_df.loc[i, 'Cartao'] = error[10]
                error_df.loc[i, 'Valor'] = error[2]
                error_df.loc[i, 'TaxaMdr%'] = error[3]
                error_df.loc[i, 'TaxaEsperada%'] = expected_fee(fee, bandeira)
                error_df.loc[i, 'ValorMdr'] = error[4]
                error_df.loc[i, 'ValorLiquido'] = error[5]
                error_df.loc[i, 'Modalidade'] = error[6]
                error_df.loc[i, 'Parcelas'] = error[7]
                error_df.loc[i, 'NSU'] = error[8]
                error_df.loc[i, 'NumeroVenda'] = error[9]
                error_df.loc[i, 'Empresa'] = error[11]
        print(error_df.head())

        save_excel(error_df, path, desktop)
        return self

    def loc_sales_receives(self):
        desktop = find_desktop_path()
        path = getPath(self.empresa, self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="recebimentos-vendas", retro=self.retro)
        db = self.DB

        sql = ''
        if self.retro:
            sql = f'''
        SELECT vendas."NSU", vendas."DataVenda", COALESCE(getnet.recebiveis."DataRecebimento") AS "DataRecebimento", "Valor", vendas."TaxaMdr", vendas."ValorMdr", vendas."ValorLiquido", vendas."Modalidade", vendas."Empresa" 
        FROM getnet.vendas
		LEFT JOIN getnet.recebiveis ON vendas."NSU" = recebiveis."NSU" AND vendas."NumeroVenda" = recebiveis."NumeroVenda"
        WHERE getnet.recebiveis."NSU" IS NOT NULL;
        ''' 
        else: 
            sql = f'''
        SELECT vendas."NSU", vendas."DataVenda", COALESCE(getnet.recebiveis."DataRecebimento") AS "DataRecebimento", "Valor", vendas."TaxaMdr", vendas."ValorMdr", vendas."ValorLiquido", vendas."Modalidade", vendas."Empresa" 
        FROM getnet.vendas
		LEFT JOIN getnet.recebiveis ON vendas."NSU" = recebiveis."NSU" AND vendas."NumeroVenda" = recebiveis."NumeroVenda"
        WHERE getnet.recebiveis."NSU" IS NOT NULL AND to_char(vendas."DataVenda", \'YYYY-MM\') = \'{self.date.year}-{self.date.strftime("%m")}\';
        ''' 
        try:  
            df = db.get_db(sql)

            print(df.head())
            save_excel(df, path, desktop)
            self.counter['payments'] = df['DataVenda'].size
        except Exception as e:
            logger.error(f"\n{sql}")
            logger.error("Não há registros referentes à vendas recebidas")

        return self
          
    def loc_sales_without_receives(self):
        desktop = find_desktop_path()
        path = getPath(self.empresa, self.date, "xlsx", complete=True, 
                       create_if_not_exists=True, report_path=True, company=self.empresa,
                       report_type="vendas-sem-recebimentos", retro=self.retro)
        db = self.DB

        sql = ''
        if self.retro:
            sql = f'''
        SELECT vendas."NSU", vendas."DataVenda", COALESCE(getnet.recebiveis."DataRecebimento") AS "DataRecebimento", "Valor", vendas."TaxaMdr", vendas."ValorMdr", vendas."ValorLiquido", vendas."Modalidade", vendas."Empresa" 
        FROM getnet.vendas
		LEFT JOIN getnet.recebiveis ON vendas."NSU" = recebiveis."NSU" AND vendas."NumeroVenda" = recebiveis."NumeroVenda"
        WHERE getnet.recebiveis."NSU" IS NULL;
        ''' 
        else: 
            sql = f'''
        SELECT vendas."NSU", vendas."DataVenda", COALESCE(getnet.recebiveis."DataRecebimento") AS "DataRecebimento", "Valor", vendas."TaxaMdr", vendas."ValorMdr", vendas."ValorLiquido", vendas."Modalidade", vendas."Empresa" 
        FROM getnet.vendas
		LEFT JOIN getnet.recebiveis ON vendas."NSU" = recebiveis."NSU" AND vendas."NumeroVenda" = recebiveis."NumeroVenda"
        WHERE getnet.recebiveis."NSU" IS NULL AND to_char(vendas."DataVenda", \'YYYY-MM\') = \'{self.date.year}-{self.date.strftime("%m")}\';
        ''' 

        try:
            df = db.get_db(sql)
            print(df.head())
            save_excel(df, path, desktop)
            self.counter['not_receivables'] = df['DataVenda'].size
        except Exception as e:
            logger.error("Não há registros referentes à vendas sem recebimentos no período")

        return self
# update public.companies set cod_maquinetas = ('{"getnet":"6816197"}') where cnpj = '32868578000150';