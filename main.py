import locale
import argparse
import calendar
from datetime import datetime
from vendas.sales import SumarioVendas
from connection.fetch_api import FetchApi
from relatorio.report import RelatorioPeriodo

##--ARGPARSE
parser = argparse.ArgumentParser()
parser.add_argument("--code", nargs='?')
parser.add_argument("--m", nargs='?')
parser.add_argument("--a", nargs='?')

args = parser.parse_args()

##-- SET Initial Configs
date = datetime(2022, 5, 1) if not args.code else datetime(args.a, args.m, 1)
end_date = date.replace(day=calendar.monthrange(date.year, date.month )[1])
end_date = datetime.now() if not end_date.day > datetime.now().day else end_date
code = 6816197 if not args.code else args.code

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
#-- Busca a API
# api = FetchApi(code=code, date=date, end_date=end_date, base_url="sandBox") 
# api.get_access_token()
# api.get_vendas()

#-- Envia para o BD e exporta para excel
# SumarioVendas(code, date).perform().export()

#-- Consulta DB e faz o relatório do total de vendas mensal
(RelatorioPeriodo(code, date, retro=False)
                    .cert_fee()
                    .loc_sales_receives()
                    .loc_sales_without_receives()
                    .get_values()
                    .show())
#------------------------------------------------------------------