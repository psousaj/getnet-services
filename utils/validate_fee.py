import json
import math    
from utils.fee import fee
# import fee


data = json.dumps(fee)
# data = json.dumps(fee.fee)
data = json.loads(data)

def validate(tax:float, bandeira):
    brand = data[0][bandeira]
    for value in brand:
        for fee in value:
            comparator = value[fee]
            if math.isclose(tax, comparator, rel_tol=0.00, abs_tol=0.05):
                return (True, fee)
    return False

def expected_fee(tax:float, bandeira):
    brand = data[0][bandeira]
    for value in brand:
        for fee in value:
            comparator = value[fee]
            if math.isclose(tax, comparator, rel_tol=0.00, abs_tol=0.2):
                return comparator, fee
    return "Nenhuma taxa aproximada"      

# print(validate(0.82, 'ELO'))
# print(0.88 < 0.90)
# print(1.9019019019019 < 1.9)

