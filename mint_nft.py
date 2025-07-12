from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import json
import secrets

#Step 1: connect to testnet
w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))#connect
assert w3.is_connected(), "Failed to connect"#test connection

#Step 2: Inject Middleware
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

#Step 3: Load abi
with open('NFT.abi', 'r') as opened_file: 
    abi = json.load(opened_file)

#Step 4: get contract
contract = w3.eth.contract(
    address = "0x85ac2e065d4526FBeE6a2253389669a12318A412",
    abi = abi
)

#Step 5: Setting up the account
privateKey = "a79d513de7ecaa28514dbff0d1f5c84acc481cb00c9948d241fca21f4abc03ff"
account = w3.eth.account.from_key(privateKey)
myAddress = account.address
print(f"Balance: {w3.from_wei(w3.eth.get_balance(myAddress), 'ether')} AVAX")

#Step 5: Mint the NFT using the "claim" Function
success = False
attemptCount = 1
gasPrice = w3.eth.gas_price
while not success:
    try: 
        nonce = secrets.token_bytes(32)        
        #build transaction
        tx = contract.functions.claim(myAddress, nonce).transact({
            'from': myAddress,
            'gas':3000000
        })

        #sign transaction
        signedTx = w3.eth.account.sign_transaction(tx, privateKey)
        txHash = w3.eth.send_raw_transaction(signedTx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(txHash)

        if receipt.status == 1: 
            success = True
            print("Minted: ", nonce)
            break
       
    except Exception as e: 
        print(attemptCount)
        attemptCount+=1
        continue

