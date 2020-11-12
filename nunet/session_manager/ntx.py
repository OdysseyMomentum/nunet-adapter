from web3 import Web3
import json
import time
import configparser as cp
class ntx():
    def __init__(self):
        self.config=cp.ConfigParser()
        self.config.read("config.ini")
        self.private_key=self.config["CONFIG"].get("private_key")
        self.public_key=self.config["CONFIG"].get("public_key")
        self.contract_address=self.config["CONFIG"].get("contract_address")
        self.infura_key=self.config["CONFIG"].get("infura_key")
        self.web3=Web3(Web3.HTTPProvider(self.infura_key))
        self.abi=json.load(open("abi.json", "r"))["abi"]
        self.contract=self.web3.eth.contract(address=Web3.toChecksumAddress(self.contract_address),abi=self.abi)

    def mine(self,value):
        nonce=self.web3.eth.getTransactionCount(self.public_key)
        tx = self.contract.functions.new_token(value).buildTransaction({
            'gas': 70000,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'nonce': nonce,
            })
        txn=self.transaction(tx)
        return txn
    
    def transfer(self,value,public_key):
        value*=10**18
        nonce=self.web3.eth.getTransactionCount(self.public_key)
        tx = self.contract.functions.transfer(public_key,value).buildTransaction({
            'gas': 70000,
            'gasPrice': self.web3.toWei('1', 'gwei'),
            'nonce': nonce,
         })
        txn=self.transaction(tx)
        return txn

    def get_balance(self,public_key):
        balance = self.contract.functions.balanceOf(public_key).call()
        balance//=10**18
        return balance
    
    def transaction(self,tx):
        signed_tx=self.web3.eth.account.signTransaction(tx,self.private_key)
        tx_hash=self.web3.eth.sendRawTransaction(signed_tx.rawTransaction)
        txn=None
        while txn==None:
            time.sleep(30)
            try:
                txn=self.web3.eth.getTransactionReceipt(tx_hash)
            except:
                pass
        return txn        
