import locale
import argparse
import calendar
from datetime import datetime
from configs.validations import * 
from connection.fetch_api import FetchApi
from configs.logging_config import logger

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
##--ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("--code", nargs='?')
parser.add_argument("--m", nargs='?')
parser.add_argument("--a", nargs='?')

args = parser.parse_args()

##-- SET Initial Configs
date = datetime.datetime(2023, 1, 1) if not args.code else datetime(args.m, args.a, 1)
end_date = date.replace(day=calendar.monthrange(date.year, date.month )[1])
end_date = datetime.datetime.now() if not end_date.day > datetime.datetime.now().day else end_date
code = 36424170 if not args.code else args.code

##--- Init
api = FetchApi(date, end_date, base_url='sandBox', code=code)
api.get_access_token()

#---- Essa parte serve para fazer a consulta do status de acesso passando o código como argumento
path = getPath(api.code, api.date, "json", complete=True, access_path=True)
data = load_json(path)

api.get_status_client(data['requestId'])
