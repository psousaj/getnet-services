import traceback
import psycopg2
import pandas as pd
import warnings
from configs.validations import *
from configs.logging_config import logger


class EmptyDataFrameException(Exception):
    def __init__(self, message):
        self.message = message

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

    def send(self, table:str, *args):
        """Envia os dados informados por parâmetro para o banco de dados

        Args:
           - data (str): Dados do json passado em String
        """        
        cur = self.cursor
        con = self.con
        lista = tuple(list(*args))

        placeholders = ", ".join(["%s"] * len(*args))
        sql = f"INSERT INTO getnet.{table} VALUES ({placeholders})"

        try:
            cur.execute(sql, lista) 
            con.commit()
            logger.info(f"{lista}")
            logger.debug("-"*20)
        except Exception:
                logger.info(f"Violação de Constraint, registro já salvo no banco de dados")

    def send_vendas(self, *args):
        cur = self.cursor
        con = self.con
        lista = tuple(list(*args))

        placeholders = ", ".join(["%s"] * len(*args))
        sql = f"INSERT INTO getnet.vendas VALUES ({placeholders})"

        try:
            cur.execute(sql, lista) 
            con.commit()
            logger.info(f"{lista}")
            logger.debug("-"*10)
        except Exception:
                logger.info(f"Violação de Constraint, registro já salvo no banco de dados")
                

    def get_db(self, sql, type=None):
        """Busca os registros referentes ao código do cliente e ao mês informado

        Args:
           - sql (str): Consulta sql em formato de string

        Returns:
           - {df.DataFrame}: Retorna um DataFrame Pandas
        """
        con = psycopg2.connect(host="192.168.1.54", user="postgres",
                            password="1234", database='DataBaseTax')
        df = pd.read_sql(f"{sql}", con=con)
        
        if df.size == 0 or df.size is None:
                raise EmptyDataFrameException("Dataframe vazio, verifique a cláusula SQL")
        return df
        
    
    def execute(self, sql:str, list=False):
        cur = self.cursor
        cur.execute(sql)

        if list:
             return cur.fetchall()
        return cur.fetchone()