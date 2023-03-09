import psycopg2
import pandas as pd
import warnings
from configs.validations import *
from configs.logging_config import logger


class Connect:

    def __init__(self):
        host = "192.168.1.54"
        user = "postgres"
        password = "1234"
        database = 'DataBaseTax'
        self.con = psycopg2.connect(host=host, user=user,
                            password=password, database=database)
        self.cursor = self.con.cursor()
        warnings.simplefilter("ignore", UserWarning)
        logger.info(f"Conexão com {database} em: {host}")

    def send(self, data):
        """Envia os dados informados por parâmetro para o banco de dados

        Args:
           - data (str): Dados do json passado em String
        """        
        cur = self.cursor
        con = self.con
        
        data = json.loads(data)
        for entry in data:
            sql = """INSERT INTO getnet.vendas
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            try:
                cur.execute(sql, (entry['cod_empresa'], entry['DataVenda'], entry['Valor'],
                              entry['TaxaMdr'], entry['ValorMdr'], entry['ValorLiquido'],
                              entry['Modalidade'], entry['Parcelas'], entry['Status'],
                              entry['NSU'], entry['NumeroVenda'], entry['Cartao']))

                con.commit()
            except Exception:
                logger.info(f"Violação de Constraint, registro já salvo no banco de dados")

    def send_vendas(self, *args):
        cur = self.cursor
        con = self.con
        lista = tuple(list(*args))

        placeholders = ", ".join(["%s"] * len(*args))
        sql = f"INSERT INTO getnet.vendas VALUES ({placeholders})"

        try:
            logger.debug("-"*10)
            logger.info(f"{sql}")
            logger.info(f"{lista}")
            logger.debug("-"*10)
            cur.execute(sql, lista) 
            con.commit()
        except Exception:
                logger.info(f"Violação de Constraint, registro já salvo no banco de dados")

    def get_db(self, sql):
        """Busca os registros referentes ao código do cliente e ao mês informado

        Args:
           - sql (str): Consulta sql em formato de string

        Returns:
           - {df.DataFrame}: Retorna um DataFrame Pandas
        """
        con = psycopg2.connect(host="192.168.1.54", user="postgres",
                               password="1234", database='DataBaseTax')
        df = pd.read_sql(f"{sql}", con=con)
        return df
    
    def execute(self, sql:str):
        cur = self.cursor

        cur.execute(sql)