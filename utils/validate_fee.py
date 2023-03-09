import json    
# from utils.fee import fee
import fee


# data = json.dumps(fee)
data = json.dumps(fee.fee)
data = json.loads(data)

def validate(tax:float, bandeira, mod):
    value = data[bandeira][mod]
    if value == tax:
        return True, mod
    elif value >= (tax - 0.02) and value <= (tax+0.3):
        return True, mod
    else:
        return False
# print(data['visa'])
print(validate(3.0900000000000034, 'VISA', 'CREDITO'))

# print(2.52 >= 2.49-0.02)
# print(2.49-0.02)