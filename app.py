from datetime import timedelta

from flask import Flask
from web3 import Web3
from flask_cors import CORS

import config as config
import utils

app = Flask(__name__)
CORS(app)
w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
token_contract = w3.eth.contract(config.TOKEN_ADDRESS, abi=config.TOKEN_ABI)
crowdsale_contract = w3.eth.contract(config.CROWDSALE_ADDRESS, abi=config.CROWDSALE_ABI)


@utils.TimedLruCache(expiration=timedelta(minutes=config.UPDATE_INTERVAL_MINUTES))
def fetchTotalSupply():
    return str(token_contract.functions.totalSupply().call())


@utils.TimedLruCache(expiration=timedelta(minutes=config.UPDATE_INTERVAL_MINUTES))
def fetchCrowdsaleRaisedWei():
    return str(crowdsale_contract.functions.weiRaised().call())


@utils.TimedLruCache(expiration=timedelta(minutes=config.UPDATE_INTERVAL_MINUTES))
def fetchCrowdsaleRaisedTokens():
    return str(int(fetchCrowdsaleRaisedWei()) * int(crowdsale_contract.functions.rate().call()))


@utils.TimedLruCache()
def fetchCrowdsaleCap():
    return str(crowdsale_contract.functions.cap().call())


# endpoints
@app.route('/totalSupply')
def getTotalSupply():
    return fetchTotalSupply()


@app.route('/crowdsaleRaisedWei')
def getCrowdsaleRaisedWei():
    return fetchCrowdsaleRaisedWei()


@app.route('/crowdsaleRaisedTokens')
def getCrowdsaleRaisedTokens():
    return fetchCrowdsaleRaisedTokens()


@app.route('/crowdsaleCap')
def getCrowdsaleCap():
    # cap is the maximum amount of wei accepted in the crowdsale
    return fetchCrowdsaleCap()


if __name__ == '__main__':
    app.run()
