from datetime import datetime
from utils.validate_fee import *
from configs.logging_config import logger
from connection.connectdb import Connect

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
        for i, reg in enumerate(df['TaxaMdr']):
            bandeira_normal = df.loc[i, 'Bandeira']
            bandeira = bandeira_normal
            mod = df.loc[i, 'Modalidade']
            bandeira = bandeira.replace(" CRÉDITO", "")
            bandeira = bandeira.replace(" DÉBITO", "")
            bandeira = str(bandeira)
            palavras = mod.split()
            indice = palavras.index("CREDITO") if palavras.__contains__("CREDITO") else palavras.index("DEBITO")
            mod = ' '.join(palavras[:indice+1])

            print(reg, bandeira_normal, validate(reg, bandeira, mod))

# update public.companies set cod_maquinetas = ('{"getnet":"6816197"}') where cnpj = '32868578000150';