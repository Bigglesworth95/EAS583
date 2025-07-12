from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

#Step 1: connect to testnet
#Notes: Fuji + Eth are EVM compatible --> Eth style provider
#Http Provider connects to a node via http w/ Fuji RPC endpoint

w3 = Web3(Web3.HTTPProvider("https://api-avax-test.network/ext/bc/C/rpc"))#connect
assert w3.is_connected(), "Failed to connect"#test connection

#Step 2: Inject Middleware (Proof of Authority)
#Notes: Avalanche uses PoA consensus for testnets; need middleware to work w/ Avalanche
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

#Step 3: Load NFT Contract
#Notes: make a python object to interact w/contract --> w3.eth.contract
#address = contract's address (from assignment)
#abi: used to call contract functions; exlains what functions do

with open('NFT.abi', 'r') as opened_file: 
    abi = json.load(opened_file)

contract = w3.eth.contract(
    address = "0x85ac2e065d4526FBeE6a2253389669a12318A412",
    abi = abi
)

#Step 4: Setting up the account
#Notes: establisng my account via my private key to actually get the NFT
private_key = "a79d513de7ecaa28514dbff0d1f5c84acc481cb00c9948d241fca21f4abc03ff"
account = w3.eth.account.from_key(private_key)
my_address = account.address

#Step 5: Mint the NFT using the "claim" Function
#Notes: claim(nonce) mints an NFT with tokenId = keccak256(nonce) % maxId
#brute force through nonces (1, 2...) until success
#test locally; then run only when successful
success = False
nonce = 1
while not success:
    nonce_bytes = nonce.to_bytes(32, 'big')
    try: 
        token_id = contract.functions.claim(my_address, nonce_bytes).call({'from': my_address})

        #build transaction
        tx = contract.functions.claim(my_address, nonce_bytes).build_transaction({
            'from': my_address,
            'nonce': w3.eth.get_transaction_count(my_address),
            'gas': 300000,  # didn't know what to put; got this # from reddit
            'gasPrice': w3.eth.gas_price
        })

        #sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1: 
            success = True
            break
        else: 
            nonce+=1
    except Exception as e: 
        continue

