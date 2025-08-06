from web3 import Web3
from web3.providers.rpc import HTTPProvider
import csv
import json

try: 
    with open("erc20s.csv", "r") as f: 
        lines = f.readlines()
except Exception as e: 
    print(e)

tokens = []
for line in lines: 
    line = line.split(",")
    if line[0] == "chain":
        continue
    else:
        chain = line[0].strip()
        address = line[1].strip()
    

    
    tokens.append((chain, address))

private_key = "a79d513de7ecaa28514dbff0d1f5c84acc481cb00c9948d241fca21f4abc03ff"

#connect to testnet RPC
avax_rpc = "https://api.avax-test.network/ext/bc/C/rpc"
bnb_rpc = "https://data-seed-prebsc-1-s1.binance.org:8545/"
avax_w3 = Web3(HTTPProvider(avax_rpc))
bnb_w3 = Web3(HTTPProvider(bnb_rpc))


#get abi
with open("contract_info.json") as f:
    info = json.load(f)

#get contract info
source_abi = info["source"]["abi"]
source_addr = info["source"]["address"]

dest_abi = info["destination"]["abi"]
dest_addr = info["destination"]["address"]

#get contracts
srcContract = avax_w3.eth.contract(abi = source_abi, address = source_addr)
destContract = bnb_w3.eth.contract(abi=dest_abi, address=dest_addr)

#get account
avax_acct = avax_w3.eth.account.from_key(private_key)
avaxAddress = avax_acct.address
bnb_account = bnb_w3.eth.account.from_key(private_key)
bnbAddress = bnb_account.address
avaxNonce = avax_w3.eth.get_transaction_count(avaxAddress)
bnbNonce = bnb_w3.eth.get_transaction_count(bnbAddress)

num=1
for token in tokens:
    tokenAddress = token[1]

    if token[0].strip() == "avax":
        tx = srcContract.functions.registerToken(tokenAddress).build_transaction({
            'from': avaxAddress,
            'nonce': avaxNonce,
            'gas': 15000000,
            'gasPrice': avax_w3.eth.gas_price,
            'chainId': 43113
        })

        signedTx = avax_w3.eth.account.sign_transaction(tx, private_key)
        txHash = avax_w3.eth.send_raw_transaction(signedTx.raw_transaction)
        receipt = avax_w3.eth.wait_for_transaction_receipt(txHash)
        avaxNonce +=1
        print(f"Tried to register token {tokenAddress} on chain {token[0]} with nonce {avaxNonce}")
        print("TX Hash: ", txHash.hex())
        print("Reciept Status: ", receipt.status)

    else:
        tx = destContract.functions.createToken(tokenAddress, f"bridgeToken{num}", "symbol{num}").build_transaction({
            "from": bnbAddress, 
            "nonce": bnbNonce, 
            "gas": 15000000, 
            "gasPrice": bnb_w3.eth.gas_price,
            "chainId": 97
        })

        signedTx = bnb_w3.eth.account.sign_transaction(tx, private_key)
        txHash = bnb_w3.eth.send_raw_transaction(signedTx.raw_transaction)
        receipt = bnb_w3.eth.wait_for_transaction_receipt(txHash)
        bnbNonce +=1
        print(f"Tried to register token {tokenAddress} on chain {token[0]} with nonce {bnbNonce}")
        print("TX Hash: ", txHash.hex())
        print("Reciept Status: ", receipt.status)
    num+=1

