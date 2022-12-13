import yaml

from blockchain import *
from Miner import Miner
from utils import *
from Wallet import Wallet

import random
wallet = Wallet()

config = yaml.load(open('config.yml'), Loader=yaml.FullLoader)
blockchain = Blockchain(config=config["blockchain"])

miner = Miner(config=config["miner"])
# tx = wallet.create_transaction(wallet.get_addr(), 50)
# print(tx)
# print(blockchain.validate_transaction(tx))
class txout:
    def __init__(self, amount: int) -> None:
        self.__amount = amount

    def get_amount(self) -> int:
        return self.__amount

    def __repr__(self) -> str:
        return f"txout(amount = {self.get_amount()})"

# Input
utxo_set = blockchain.get_UTXO_set()
for i in range (10):
    utxo_set[(b'random hash', i)] = txout(amount=random.randint(10, 100))

coin_amount = 150

# Code
selected_utxo = {}
coin_list = []
sum = 0
#def fifo_selection(list,amount):

for key in utxo_set.keys():
    #print(key,'->',utxo_set[key])
    coin = utxo_set[key].get_amount()
    #print(coin)
    coin_list.append(coin)
    for i in range(len(coin_list)):
        sum += coin_list[i]
        #...st wronggg :'((
        if sum < coin_amount:
            print(sum)
            selected_utxo.update({key:coin})
print(coin_list)        
# Output
# return selected_utxo
print(selected_utxo)
