import hashlib
import time
import json
import os
from flask import Flask, jsonify, request, render_template

# Block Class to define the structure of a single block
class Block:
    def __init__(self, index, previous_hash, data, timestamp):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp
        self.hash = self.calculate_hash()

    # Calculate the hash of the block based on its contents
    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.data}{self.timestamp}"
        return hashlib.sha256(block_string.encode()).hexdigest()

# Blockchain Class to manage the chain of blocks
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    # Create the first (genesis) block
    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block", time.time())

    # Get the most recent block in the chain
    def get_latest_block(self):
        return self.chain[-1]

    # Add a new block to the blockchain
    def add_block(self, new_block):
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = new_block.calculate_hash()
        self.chain.append(new_block)

    # Validate the integrity of the blockchain by checking hashes
    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if the current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False

            # Check if the block is properly linked to the previous one
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

# Flask Web App
app = Flask(__name__)

# Initialize a blockchain
blockchain = Blockchain()

# Serve the landing page
@app.route('/')
def home():
    return render_template('index.html')

# Get the full blockchain
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'previous_hash': block.previous_hash,
            'hash': block.hash,
            'data': block.data,
            'timestamp': block.timestamp
        })
    response = {
        'length': len(chain_data),
        'chain': chain_data,
        'valid': blockchain.is_chain_valid()
    }
    return jsonify(response), 200

# Add a new block with data
@app.route('/mine', methods=['POST'])
def mine_block():
    data = request.json.get('data')
    if not data:
        return jsonify({'error': 'Data is required'}), 400

    # Create a new block and add it to the blockchain
    new_block = Block(len(blockchain.chain), blockchain.get_latest_block().hash, data, time.time())
    blockchain.add_block(new_block)

    return jsonify({
        'message': 'Block mined successfully',
        'index': new_block.index,
        'hash': new_block.hash,
        'previous_hash': new_block.previous_hash,
        'data': new_block.data,
        'timestamp': new_block.timestamp
    }), 201

# Run the Flask app
if __name__ == '__main__':
    # Get the port from the environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    app.run(port=port)
