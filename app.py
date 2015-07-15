import json
from flask import Flask, render_template, request

app = Flask(__name__)

MLPUBKEY_PATH = 'keys/ml-certs-public-key.asc'
TXIDMAP_PATH = 'data/transaction_id_mappings.json'

def read_json(path):
	with open(path) as json_file:
		data = json.load(json_file)
	json_file.close()
	return data 

def read_file(path):
	with open(path) as f:
		data = f.read()
	f.close()
	return data
 
def get_txid(data,id):
	return data[id]

def check_display(award):
	if award['display'] == 'FALSE':
		award['subtitle'] = '';
	return award

@app.route('/')
def home_page():
	return render_template('index.html')

@app.route('/keys/ml-certs-public-key.asc')
def mlpubkey_page():
	content = read_file(MLPUBKEY_PATH)
	return content

@app.route('/<id>')
def award(id=None):
	if id:
		pubkey_content = read_file(MLPUBKEY_PATH)
		txidmap_content = read_json(TXIDMAP_PATH)
		tx_id = get_txid(txidmap_content,id)
		try:
			recipient = read_json('data/jsons/'+id+'.json')
		except IOError:
			return 'Invalid URL'	
		if recipient:
			award = {
				"logoImg": recipient["certificate"]["issuer"]["image"],
				"name": recipient["recipient"]["givenName"]+' '+recipient["recipient"]["familyName"],
				"title": recipient["certificate"]["title"],
				"subtitle": recipient["certificate"]["subtitle"]["content"],
				"display": recipient["certificate"]["subtitle"]["display"],
				"organization":recipient["certificate"]["issuer"]["name"],
				"text": recipient["certificate"]["description"],
				"signatureImg": recipient["assertion"]["image:signature"],
				"mlPublicKey": pubkey_content,
				"mlPublicKeyURL": recipient["verify"]["signer"],
				"transactionID": tx_id,
				"transactionIDURL": 'https://blockchain.info/tx/'+tx_id
			}
			award = check_display(award)
			return render_template('award.html', award=award)
	else:
		return "Error, please try again."

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)