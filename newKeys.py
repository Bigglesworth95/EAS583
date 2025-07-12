from web3 import Web3
w3 = Web3()
account = w3.eth.account.create()
private_key = account.key.hex()  # Hex format without 0x
with open("secret_key.txt", "w") as f:
    f.write(private_key)
print("Address:", account.address)