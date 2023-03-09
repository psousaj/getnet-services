import sys
import warnings
import requests
from datetime import datetime
from configs.validations import * 
from configs.logging_config import *
from connection.access.manage import FetchAccess


class FetchApi:
    path = isUnix(get_config_path())
    data = load_web_json(path)

    def __init__(self, date:datetime.datetime, end_date:datetime.datetime, code=13381369, base_url=''):
        if base_url == 'sandBox':
            string = "\nIsso é um teste em ambiente SandBox, dúvidas? entre em contato com o administrador do sistema"
            warnings.warn(string)
            self.base_url = 'https://rl7-sandbox-api.useredecloud.com.br'
        else:
            self.base_url = 'https://api.userede.com.br/redelabs'
        self.date = date
        self.start_date = date.strftime("%Y-%m-%d")
        self.end_date = end_date.strftime("%Y-%m-%d")
        self.code = code
        
        # -- ENDPOINTS
        self.vendas_uri = f'{self.base_url}/merchant-statement/v1/sales?parentCompanyNumber={self.code}&subsidiaries={self.code}&startDate={self.start_date}&endDate={self.end_date}'
        self.parcelas_uri = f'{self.base_url}/merchant-statement/v1/sales/installments?parentCompanyNumber={self.code}&subsidiaries={self.code}&startDate={self.start_date}&endDate={self.end_date}'
        self.recebiveis_uri = f'{self.base_url}/merchant-statement/v1/receivables?parentCompanyNumber={self.code}&subsidiaries={self.code}&startDate={self.start_date}&endDate={self.end_date}'
        logger.debug(f'{date.strftime("%d/%m/%Y")} até {end_date.strftime("%d/%m/%Y")}')
        logger.info("API REDE Inicializada com sucesso")
        logger.info(self.base_url)

        # -- Credenciais
        self.client_id = self.data[0]['ClientId'] if base_url == 'sandBox' else self.data[1]['ClientId']
        self.client_secret = self.data[0]['ClientSecret'] if base_url == 'sandBox' else self.data[1]['ClientSecret']
        self.username = self.data[0]['Username'] if base_url == 'sandBox' else self.data[1]['Username']
        self.password = self.data[0]['Password'] if base_url == 'sandBox' else self.data[1]['Password']
        self.access_token = ' '
        self.refresh_token = ' '

    def get_access_token(self):
        """Gera o access token necessário em cada requisição da API

        Returns:
           - {self} : Retorna a própria instância da classe. (permite action chaining)
        """
        logger.info("gerando access_token")
        url = f'{self.base_url}/oauth/token'
        payload = {'grant_type': 'client_credentials', 'username': self.username, 'password': self.password}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8'}  # , 'Authorization': 'Basic MDZjMGQxYjItNDY2ZS00MmEwLWIzZTMtMjBhYjJlZDc5MzExOnQ3bnM0NmNoc2k='

        ##--- Is a valid date? 
        try:
            is_future_date(self.date)
        except Exception as e:
            logger.error(str(e))
            sys.exit()

        response = requests.post(url, data=payload, headers=headers, auth=(self.client_id, self.client_secret))  #
        if response.status_code == 200:
            response = response.json()

            self.access_token = response['access_token']
            self.refresh_token = None if not self.base_url == 'sandBox' else response['refresh_token']

            self.data[1]['access_token'] = self.access_token
            self.data[1]['refresh_token'] = None if not self.base_url == 'sandBox' else response['refresh_token']
            
            send_json(self.path, self.data)

            logger.info("--" * 20)
            logger.info(response)
            logger.info("--" * 20)
        else:
            logger.error(f"Erro na requisição do access_token {response}")
            logger.error(f"{response.json()['message']}, code:{response.status_code}")
        return self

    def update_token(self):
        """A API precisa resetar o token de acesso a cada 24 minutos.
        Esse método faz a requição do novo token e o armazena no atributo da instancia
        """
        logger.info("gerando novo access_token com refresh")
        url = f'{self.base_url}/oauth/token'
        payload = {'grant_type': 'refresh_token', 'refresh_token': self.refresh_token}

        response = requests.post(url, data=payload, auth=(self.client_id, self.client_secret))  #
        if response.status_code == 200:
            response = response.json()
            self.access_token = response['access_token']
            self.refresh_token = response['refresh_token']
            logger.info("--" * 20)
            logger.info(response)
            logger.info("--" * 20)
        else:
            logger.error(f"Erro na requisição do refresh_token {response}")
            logger.error(response.text)

    def permit_client(self, requestType='T', permissions='R', filiates:int=[], consult_after_request=False):
        """Solicita acesso a um cliente especificado pelo código

        Args:
           - requestType (str, optional): T: total, P, Parcial, I: .... Defaults to 'T'.
           - permissions (str, optional): R: Leitura, W: Modficação. Defaults to 'R'.
           - filiates (list, optional): Lista de filiais desta empresa (refere-se ao código). Defaults to vazio [].
           - consult_after_request (bool, optional): Informe true se quiser consultar o status de acesso em seguida. Defaults to False.
        """
        logger.info(f"solicitando acesso aos dados do cliente: {self.code}")
        api = FetchAccess(self.access_token, self.code, self.base_url)

        if consult_after_request:
            api.create_access(self.date, requestType, permissions, filiates).get_status()

        api.create_access(self.date, requestType, permissions, filiates)

    def get_status_client(self, requestId):
        """Consulta status de acesso a um cliente específico pelo cód

        Args:
            - requestId (str): requestId localizado no arquivo baixado do servidor ao solicitar acesso
        """
        logger.info(f"requisitando status de acesso cliente: {self.code}")
        FetchAccess(self.access_token, self.code, self.base_url).get_status(requestId)

    def get_vendas(self):
        """Requisita arquivo com os dados de vendas do cliente informado pelo cód.
        A resposta é um json salvo no diretório connection/files
        """
        logger.info(f"buscando informações de vendas cliente: {self.code}")
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(self.vendas_uri, headers=headers)

        if response.status_code == 200:
            response = response.json()

            path = getPath(self.code, self.date, "json", complete=True, create_if_not_exists=True)
            save_json(path, response)

            logger.info(f"Arquivo de vendas baixado com sucesso em:\n{path}")
        else:
            logger.error("Erro interno")
            logger.error(f'{response.json()["message"]} code:{response.status_code}')
            logger.info('--' * 20)
