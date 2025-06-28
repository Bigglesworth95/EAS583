import requests
import json



def pin_to_ipfs(data):
	assert isinstance(data,dict), f"Error pin_to_ipfs expects a dictionary"
	url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
	
	payload = {	"pinataOptions": {"cidVersion": 1},
			"pinataMetadata": {"name": "test"},
			"pinataContent": data
			}

	headers = {
	"pinata_api_key": "ff87d301f7720c766fb4",
	"pinata_secret_api_key": "472f90bfd93a12367128c702f89e70603074985d12c3d0738b1b493bc17bf0fb",
	"Content-Type": "application/json"
	}

	response = requests.request("POST", url, json=payload, headers=headers)

	cid = response.json().get("IpfsHash")
	return cid

def get_from_ipfs(cid,content_type="json"):
	assert isinstance(cid,str), f"get_from_ipfs accepts a cid in the form of a string"
	#YOUR CODE HERE
	url = f"https://gateway.pinata.cloud/ipfs/{cid}"
	response = requests.get(url)
	data = response.json()

	assert isinstance(data,dict), f"get_from_ipfs should return a dict"
	return data
