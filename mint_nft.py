rom web3 import Web3
from web3.middleware import geth_poa_middleware
import json

#Step 1: connect to testnet
w3 = Web3(Web3.HTTPProvider("https://api-avax-test.network/ext/bc/C/rpc"))#connect
assert w3.is_connected(), "Failed to connect"#test connection

#Step 2: Inject Middleware
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

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
account = w3.eth.account.from_key(private_key)
myAddress = account.address

#Step 5: Mint the NFT using the "claim" Function
#increment thru nonces until success = True
success = False
attemptCount = 1
while not success:
    nonce = attemptCount.to_bytes(32, 'big')
    try: 
        tokenId = contract.functions.claim(myAddress, nonce).call({'from': myAddress})

        #build transaction
        tx = contract.functions.claim(myAddress, nonce).build_transaction({
            'from': myAddress,
            'nonce': w3.eth.get_transaction_count(myAddress),
            'gas': 300000,  # didn't know what to put; got this # from reddit
            'gasPrice': w3.eth.gas_price
        })

        #sign transaction
        signedTx = w3.eth.account.sign_transaction(tx, privateKey)
        txHash = w3.eth.send_raw_transaction(signedTx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(txHash)

        if receipt.status == 1: 
            success = True
            break
        else: 
            nonce+=1
    except Exception as e: 
        continue

