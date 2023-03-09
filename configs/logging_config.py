import logging
import logging.config

class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.classname = record.name
        return super().format(record)

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Criando um handler para o log no terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Criando um handler para o log em arquivo de texto
file_handler = logging.FileHandler('logs.txt')
file_handler.setLevel(logging.DEBUG)

# Definindo o formato das mensagens de log 
formatter = CustomFormatter('%(asctime)s - %(classname)s -%(levelname)s- %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adicionando os handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

