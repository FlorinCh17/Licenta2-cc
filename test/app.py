from flask import Flask, jsonify, request
from wallet import Wallet
from blockchain import Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200


@app.route('/create_entity', methods=['POST'])
def create_entity():
    # Call the wallet class to create a new entity and wallet
    data = request.get_json()
    if 'name' in data and 'place_of_b' in data:

        new_wallet = Wallet()
        response = {
                "address": new_wallet.address,
                "name": data['name'],
                "place_of_birth": data["place_of_b"],
                "CNP": new_wallet.identity,
##              "health": new_wallet.generateHealthInfo()
}
        return jsonify(response), 201

    else:
        response = {'message': 'Cerere invalida. Includeti suprafata, locatia si adresa detinatorului in cererea dumneavoastra POST.'}
        return jsonify(response), 400


# Running the app
app.run(host = '0.0.0.0', port = 5000)

