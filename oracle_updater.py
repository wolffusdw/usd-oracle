import os
import requests
from tronpy import Tron
from tronpy.keys import PrivateKey

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
OWNER_ADDRESS = os.getenv("OWNER_ADDRESS")

ORACLE_URL = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=usd"

client = Tron(network='mainnet')

def get_usdt_price():
    try:
        response = requests.get(ORACLE_URL)
        data = response.json()
        price = data['tether']['usd']
        return int(price * 1_000_000)
    except Exception as e:
        print("Erro ao obter preço:", e)
        return None

def update_contract(rate):
    try:
        contract = client.get_contract(CONTRACT_ADDRESS)
        pk = PrivateKey(bytes.fromhex(PRIVATE_KEY))
        txn = (
            contract.functions.updateFromOracle(rate)
            .with_owner(OWNER_ADDRESS)
            .fee_limit(5_000_000)
            .build()
            .sign(pk)
        )
        result = txn.broadcast().wait()
        print("✅ Atualizado com sucesso:", result['txid'])
    except Exception as e:
        print("Erro ao enviar transação:", e)

if __name__ == '__main__':
    rate = get_usdt_price()
    if rate:
        print("📡 Atualizando contrato com taxa:", rate)
        update_contract(rate)
    else:
        print("❌ Cotação inválida")
