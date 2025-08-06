from web3 import Web3
from web3.providers.rpc import HTTPProvider
from web3.middleware import ExtraDataToPOAMiddleware #Necessary for POA chains
from datetime import datetime
import json


def connect_to(chain):
    if chain == 'source':  # The source contract chain is avax
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'destination':  # The destination contract chain is bsc
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['source','destination']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    return w3


def get_contract_info(chain, contract_info):
    """
        Load the contract_info file into a dictionary
        This function is used by the autograder and will likely be useful to you
    """
    try:
        with open(contract_info, 'r')  as f:
            contracts = json.load(f)
        abiFuncs = [entry['name'] for entry in contracts[chain]['abi'] if entry ['type'] == 'function']
        print(f"Loaded ABI for {chain}: {abiFuncs}")
    except Exception as e:
        print( f"Failed to read contract info\nPlease contact your instructor\n{e}" )
        return 0
    return contracts[chain]



def scan_blocks(chain, contract_info="contract_info.json"):
    """
        chain - (string) should be either "source" or "destination"
        Scan the last 5 blocks of the source and destination chains
        Look for 'Deposit' events on the source chain and 'Unwrap' events on the destination chain
        When Deposit events are found on the source chain, call the 'wrap' function the destination chain
        When Unwrap events are found on the destination chain, call the 'withdraw' function on the source chain
    """

    # This is different from Bridge IV where chain was "avax" or "bsc"
    if chain not in ['source','destination']:
        print( f"Invalid chain: {chain}" )
        return 0
        #YOUR CODE HERE

    #connect to the chains
    listenerW3 = connect_to(chain)
    activeChain = "source" if chain == "destination" else "destination"
    activeW3 = connect_to(activeChain)

    #get the abi & address info
    listenerContractInfo = get_contract_info(chain, contract_info)
    activeContractInfo = get_contract_info(activeChain, contract_info)
    #get the contract
    listenerContract = listenerW3.eth.contract(abi = listenerContractInfo["abi"], address = listenerContractInfo["address"])
    activeContract = activeW3.eth.contract(abi = activeContractInfo["abi"], address = activeContractInfo["address"])

    #get accounts
    privateKey = "a79d513de7ecaa28514dbff0d1f5c84acc481cb00c9948d241fca21f4abc03ff"
    listenerAccount = listenerW3.eth.account.from_key(privateKey)
    listenerAccountAddress = listenerAccount.address
    listenerNonce = listenerW3.eth.get_transaction_count(listenerAccountAddress)

    activeAccount = activeW3.eth.account.from_key(privateKey)
    activeAccountAddress = activeAccount.address
    activeNonce = activeW3.eth.get_transaction_count(activeAccountAddress)


    #scan
    counter = 0
    #loop thru and get the info from each block
    while counter <= 4: 
        cur_block = listenerW3.eth.block_number - counter
        if chain == "source":
            depositFilter = listenerContract.events.Deposit.create_filter(from_block=cur_block, to_block=cur_block)
            deposits = depositFilter.get_all_entries()
            for deposit in deposits:
                tokenAddress = deposit["args"]["token"]
                recipient = deposit["args"]["recipient"]
                amount = deposit["args"]["amount"]
                tx = activeContract.functions.wrap(tokenAddress, recipient, amount).build_transaction({
                    "from": activeAccountAddress, 
                    "nonce": nonce,
                    "gas": 30000, 
                    "gasPrice": activeW3.eth.gas_price,
                    "chainId": 43113
                })
                nonce+=1
                signedTx = activeW3.eth.account.sign_transaction(tx, privateKey)
                txHash = activeW3.eth.send_raw_transaction(signedTx.raw_transaction)
                receipt = activeW3.eth.wait_for_transaction_receipt(txHash)
        else:
            unwrapFilter = listenerContract.events.Unwrap.create_filter(from_block=cur_block, to_block = cur_block)
            unwraps = unwrapFilter.get_all_entries()
            for unwrap in unwraps:
                tokenAddress = unwrap["args"]["token"]
                recipient = unwrap["args"]["recipient"]
                amount = unwrap["args"]["amount"]
                tx = activeContract.functions.withdraw(tokenAddress, recipient, amount).build_transaction({
                    "from": activeAccountAddress,
                    "nonce": nonce,
                    "gas": 30000,
                    "gasPrice": activeW3.eth.gas_price,
                    "chainId": 97
                })
                nonce+=1
                signedTx = activeW3.eth.account.sign_transaction(tx, privateKey)
                txHash = activeW3.eth.send_raw_transaction(signedTx.raw_transaction)
                receipt = activeW3.eth.wait_for_transaction_receipt(txHash)
        counter +=1

