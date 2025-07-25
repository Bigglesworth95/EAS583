import random
import json
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
from web3.providers.rpc import HTTPProvider


# If you use one of the suggested infrastructure providers, the url will be of the form
# now_url  = f"https://eth.nownodes.io/{now_token}"
# alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
# infura_url = f"https://mainnet.infura.io/v3/{infura_token}"

def connect_to_eth():
	url = "https://mainnet.infura.io/v3/491788a5602c483aae2f68089dfe0c74"
	w3 = Web3(HTTPProvider(url))
	assert w3.is_connected(), f"Failed to connect to provider at {url}"
	return w3



def connect_with_middleware(contract_json):
	with open(contract_json, "r") as f:
		d = json.load(f)
		d = d['bsc']
		address = d['address']
		abi = d['abi']

	url = "https://bsc-testnet.infura.io/v3/491788a5602c483aae2f68089dfe0c74"  
	w3 = Web3(HTTPProvider(url))

	contract = w3.eth.contract(abi=abi, address=address)
	w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
	return w3, contract

def is_ordered_block(w3, block_num):
    block = w3.eth.get_block(block_num, full_transactions=True)
    transactions = block['transactions']
    if len(transactions) == 0:
        return True

    ordered = True
    parentPrice = None
	
    '''
    1. Check if the block is empty (no transactions)
    2. If the block is empty, return True (an empty block is considered ordered)
    3. If the block is not empty, iterate through the transactions in the block
    4. For each transaction, check its type (0 or 2)
    5. For type 0 transactions, compare the gasPrice of the transaction with the previous transaction's gasPrice
    6. For type 2 transactions, calculate the priority fee and compare it with the previous transaction's priority fee
    7. If any transaction is out of order, set ordered to False and break the loop
    '''
    for transaction in transactions:
        if transaction['type'] == 0:
            if parentPrice is not None and transaction['gasPrice'] > parentPrice:
                ordered = False
                break
            parentPrice = transaction['gasPrice']
        elif transaction['type'] == 2:
            maxFeePerGas = transaction['maxFeePerGas']
            maxPriorityFeePerGas = transaction['maxPriorityFeePerGas']
            baseFeePerGas = block['baseFeePerGas']
            priorityFee = min(maxPriorityFeePerGas + baseFeePerGas, maxFeePerGas)
            if parentPrice is not None and priorityFee > parentPrice:
                ordered = False
                break
            parentPrice = priorityFee

    return ordered


def get_contract_values(contract, admin_address, owner_address):
	"""
	Takes a contract object, and two addresses (as strings) to be used for calling
	the contract to check current on chain values.
	The provided "default_admin_role" is the correctly formatted solidity default
	admin value to use when checking with the contract
	To complete this method you need to make three calls to the contract to get:
	  onchain_root: Get and return the merkleRoot from the provided contract
	  has_role: Verify that the address "admin_address" has the role "default_admin_role" return True/False
	  prime: Call the contract to get and return the prime owned by "owner_address"

	check on available contract functions and transactions on the block explorer at
	https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	"""
	default_admin_role = int.to_bytes(0, 32, byteorder="big")

	onchain_root = contract.functions.merkleRoot().call()  # Get and return the merkleRoot from the provided contract
	has_role = contract.functions.hasRole(default_admin_role, admin_address).call()  # Check the contract to see if the address "admin_address" has the role "default_admin_role"
	prime = contract.functions.getPrimeByOwner(owner_address).call() # Call the contract to get the prime owned by "owner_address"

	return onchain_root, has_role, prime


"""
	This might be useful for testing (main is not run by the grader feel free to change 
	this code anyway that is helpful)
"""
if __name__ == "__main__":
	# These are addresses associated with the Merkle contract (check on contract
	# functions and transactions on the block explorer at
	# https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
	admin_address = "0xAC55e7d73A792fE1A9e051BDF4A010c33962809A"
	owner_address = "0x793A37a85964D96ACD6368777c7C7050F05b11dE"
	contract_file = "contract_info.json"

	eth_w3 = connect_to_eth()
	cont_w3, contract = connect_with_middleware(contract_file)

	latest_block = eth_w3.eth.get_block_number()
	london_hard_fork_block_num = 12965000
	assert latest_block > london_hard_fork_block_num, f"Error: the chain never got past the London Hard Fork"

	n = 5
	for _ in range(n):
		block_num = random.randint(1, latest_block)
		ordered = is_ordered_block(block_num)
		if ordered:
			print(f"Block {block_num} is ordered")
		else:
			print(f"Block {block_num} is not ordered")
