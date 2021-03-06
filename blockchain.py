import hashlib
import json
from time import time
#from urllib.parse import urlparse
from urlparse import urlparse
from uuid import uuid4
import os, sys

import requests
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import image_distance
import tempfile
import math


class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()
        self.configure = image_distance.load_model()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)
    
    def calculate_iamge_distance(self, img2_path, img1_path="/tmp/upload/yandi.jpg"):
        img1_bgrImg = cv2.imread(img1_path)
        img1_rgbImg = cv2.cvtColor(img1_bgrImg, cv2.COLOR_BGR2RGB)
 
        img2_bgrImg = cv2.imread(img2_path)
        img2_rgbImg = cv2.cvtColor(img2_bgrImg, cv2.COLOR_BGR2RGB)

        distance = image_distance.getRep(img1_rgbImg, self.configure) - image_distance.getRep(img2_rgbImg, self.configure)

        return np.dot(distance, distance)

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://%s/chain' % node)

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, filename):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
         
        :param last_block: <dict> last Block
        :return: <int>
        """

        # last_proof = last_block['proof']
        # last_hash = self.hash(last_block)

        # proof = 0
        # while self.valid_proof(last_proof, proof, last_hash) is False:
        #     proof += 1
        (valid, distance) = self.valid_proof(filename)
        if valid:
            return (valid, filename + '$' * self.reward(distance) + str(distance))
        else:
            return (valid, str(distance))

    @staticmethod
    def valid_proof(filename):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        # guess = ('%s%s%s' % (last_proof, proof, last_hash)).encode()
        # guess_hash = hashlib.sha256(guess).hexdigest()

        # return guess_hash[:4] == "0000"
        distance = blockchain.calculate_iamge_distance(filename)
        return (distance < 0.2, distance)

    def reward(self, distance):
        if distance ==  0.0:
            number_of_dollar = 10
        else: number_of_dollar = max(10, math.ceil(1.0 / distance))

        return int(number_of_dollar)

# Instantiate the Node
UPLOAD_FOLDER = '/tmp/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def error_msg(msg = None):
    if msg is not None:
        response = {"message":msg}
        pass
    else:
        response = {"message":"error"}
        pass
    return jsonify(response), 400

@app.route('/sendimage', methods=['POST'])
def sendimage():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return error_msg('No file part')
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return error_msg('No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            distance = blockchain.calculate_iamge_distance(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            response = {
                "message": "image is received",
                "filename": filename,
                "distance": distance
            }
            return jsonify(response), 200
        pass
    return error_msg()

# receive image
@app.route('/mine', methods=['POST'])
def mine():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return error_msg('No file part')
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return error_msg('No selected file')
        if file and allowed_file(file.filename):
            filename = tempfile.mkstemp(dir=app.config['UPLOAD_FOLDER'])[1]
            file.save(filename)
    
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    # proof = blockchain.proof_of_work(last_block)
    valid, proof = blockchain.proof_of_work(filename)
    if not valid: return error_msg('Invalid image with distance: ' + proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': 'Transaction will be added to Block %d' % index}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
