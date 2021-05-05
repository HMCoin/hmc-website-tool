from datetime import timedelta

from flask import Flask
from web3 import Web3
import config
import utils

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{config.INFURA_PROJECT_ID}'))
token_contract = w3.eth.contract(config.TOKEN_ADDRESS, abi=config.TOKEN_ABI)


@utils.TimedLruCache(expiration=timedelta(minutes=config.UPDATE_INTERVAL_MINUTES))
def fetchTotalSupply():
    return str(token_contract.functions.totalSupply().call())


@app.route('/totalSupply')
def getTotalSupply():
    return fetchTotalSupply()


if __name__ == '__main__':
    app.run()
