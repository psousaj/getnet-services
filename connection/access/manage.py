import requests
from configs.logging_config import logger
from configs.validations import *


class FetchAccess:

    def __init__(self, token, code, base_url):
        self.token = token
        self.requestId = ''
        self.code = code
        self.base_url = base_url

    def create_access(self, date, requestType, permissions, filiates) -> 'FetchAccess':
        """Este, é o método responsável pela implementação da logica de acesso.
        Solicita acesso a um cliente especificado pelo código

        Args:
           - requestType (str, optional): T: total, P, Parcial, I: .... Defaults to 'T'.
           - permissions (str, optional): R: Leitura, W: Modficação. Defaults to 'R'.
           - filiates (list, optional): Lista de filiais desta empresa (refere-se ao código). Defaults to vazio [].
           - consult_after_request (bool, optional): Informe true se quiser consultar o status de acesso em seguida. Defaults to False.
        """
        logger.info(f"solicitação de acesso enviada para {self.code}")
        url = f'{self.base_url}/partner/v1/organizations/requests/features/merchant-statement'
        headers = {'Authorization': f'Bearer {self.token}'}
        data = {'requestCompanyNumber': self.code, 'companyNumbers': filiates, 'requestType': requestType,
                'permissions': permissions}
        # cert_path = os.getcwd()
        # cert1 = cert_path + r"\connection\access\ssl\cloudflare.pem"
        # cert2 = cert_path + r"\connection\access\ssl\cloudflare_key.pem"
        # cert_path = (cert1, cert2)

        response = requests.post(url, headers=headers, json=data) #, cert=cert_path
        code = response.status_code

        if code == 201:
            response = response.json()
            self.requestId = response['requestId']

            path = getPath(self.code, date, "json", complete=True, access_path=True, create_if_not_exists=True)
            save_json(path, response)

            logger.info(f"Token de acesso registrado com sucesso em:\n{path}")
        else:
            logger.info("--"*20)
            logger.error(f'{response.json()["message"]} code:{code}')

        requestId = self.get_requestId() if code == 201 else response.json()['requestId']
        logger.debug("--" * 20)
        logger.debug(f'Request ID: {requestId}')

        return self

    def get_status(self, requestId:int = None) -> None:
        """
        Verifica o status da solicitação de acesso a um cliente pelo código rede dele.
        O método pode ou não receber como parâmetro o código desejado na consulta. Isso 
        serve para que ao solicitar acesso e em seguida verificar o status da solicitação, 
        não seja necessário informar o code. Caso contrário, informe o código para fazer apenas a consulta

        Args:
            - requestId(Opcional): (int) código do cliente
        """
        if requestId is not None:
            url = f'{self.base_url}/partner/v1/organizations/requests/{requestId}/features/merchant-statement'
        else:
            url = f'{self.base_url}/partner/v1/organizations/requests/{self.requestId}/features/merchant-statement'

        headers = {'Authorization': f'Bearer {self.token}'}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            logger.info("--"*20)
            response = response.json()
            logger.info(f'{response["partnerName"]}, feature:{response["feature"]}')
            logger.info(f'requestType:{response["requestType"]} permissions:{response["permission"]}')
            logger.info("--"*20)
            logger.info(f'Status da solicitação à empresa {response["partnerName"]}: {response["status"]}')
        else:
            logger.info("--"*20)
            logger.error(f'{response.json()["message"]} code:{response.status_code}')

    def get_requestId(self):
        return self.requestId
