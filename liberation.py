import locale
import argparse
import calendar
from configs.validations import *
from connection.fetch_api import FetchApi

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
##--ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("--code", nargs='?')
parser.add_argument("--consult", nargs='?')
parser.add_argument("--m", nargs='?')
parser.add_argument("--a", nargs='?')

args = parser.parse_args()

##-- SET Initial Configs
date = datetime.datetime(2023, 1, 1) if not args.code else datetime(args.m, args.a, 1)
end_date = date.replace(day=calendar.monthrange(date.year, date.month )[1])
end_date = datetime.datetime.now() if not end_date.day > datetime.datetime.now().day else end_date
consult = True if args.consult is not None else False
code = 36424170 if not args.code else args.code

##--- Init
(FetchApi(date, end_date, base_url='sandBox', code=code)
                                            .get_access_token()
                                            .permit_client(consult_after_request=consult))

# update public.companies set cod_maquinetas=('{"rede": "85071722"}') 
# where name = 'FGF COMERCIO DE DERIVADOS DE PETROLEO LTDA'