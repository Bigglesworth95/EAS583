from web3 import Web3
#Step 1: connect to avalanche with web3

#why HTTPProvider -- how to know when to use this? 
w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))
#why get_poa_middleware; how to know when to use middleware? 
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


#Step 2: load the contract using the ABI (given)

#how does this eth.contract work? 
#what does it do to load the abi -- what happens with that? 
#is it possible to view the code in the contract? 
#how would I know to do this? 
#what do I need the contract for? What am I going to do with it? 
contract = w3.eth.contract(
    address = "0x85ac2e065d4526FBeE6a2253389669a12318A412",
    abi = json.load(open('NFT.abi'))
)

#Step 3: check for token ownership
#are unclaimed tokens always having an owner of just 0? 
#How many 0's does it have to have? 

def token_is_available(tokenID):
    try: 
        owner = contract.functions.ownerOf(tokenID).call()
        return owner == '0x0000000000000000000000000000000000000000'
    except: 
        return True

#Step 4: check small token ids & move up
#how does this end up working? wont the id not be in hex? 
tokenID = 1
while not token_is_available(tokenID):
    tokenID +=1

#Step 5: Mint NFTs
#how does this work? I don't think i would think to do this ever in a million years
if math.gcd(tokenA, tokenB) == 1: 
    contract.functions.combine(tokenA, tokenB).transact()



