from flask import Flask, jsonify, request
import threading
import base64
import json
import hashlib
import datetime
import os
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import socket

# Blockchain Class
class Blockchain:
    Identity_dict= {}
    Identity_admin= {}
    Users= {}
    Identity_contestants = {}
    ToBeDetermined = {}
    Declined_users = {}
    RejectedRequests = {}

    def __init__(self, host='127.0.0.1', port=5001):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')
        self.balances = {}
        self.load_data("identity_data.json", "identity_admin_data.json", "credentials_block.json", "contestants.json", "distribute_votes.json")
        self.voting_start_date = None
        self.voting_end_date = None
        self.votes_distributed = None
        self.host = host
        self.port = port
        self.peers = []

    def set_voting_period(self, start_date, end_date):
        self.voting_start_date = start_date
        self.voting_end_date = end_date

    def load_data(self, file_name1, file_name2, file_name3, file_name4, file_name5):
        try:
            with open(file_name1, "r") as file:
                self.Identity_dict = json.load(file)
            with open(file_name2, "r") as file:
                self.Identity_admin = json.load(file)
            with open(file_name3, "r") as file:
                self.Users = json.load(file)
            with open(file_name4, "r") as file:
                self.Identity_contestants = json.load(file)
            with open(file_name5, "r") as file:
                self.votes_distributed = json.load(file)
        except FileNotFoundError:
            print("There are no files")

    def save_data(instance, file_name):
        with open(file_name, "w") as file:
            json.dump(instance, file)

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'previous_hash': previous_hash,
            'transactions': []
        }
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount, private_key):
        sender_balance = self.get_balance(sender)
        if sender_balance is None or sender_balance < amount:
            return False

        transaction = {'sender': sender, 'receiver': receiver, 'amount': amount}
        transaction_json = json.dumps(transaction, sort_keys=True).encode()
        sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        signature = sk.sign(transaction_json).hex()
        transaction['signature'] = signature

        self.decrease_balance(sender, amount)
        self.increase_balance(receiver, amount)
        self.chain[-1]['transactions'].append(transaction)
        #self.broadcast_block(self.chain[-1])  # Broadcast the block with the new transaction
        return True

    def verify_transaction(self, transaction):
        try:
            sender = transaction['sender']
            signature = bytes.fromhex(transaction['signature'])
            transaction_data = {'sender': sender, 'receiver': transaction['receiver'], 'amount': transaction['amount']}
            transaction_json = json.dumps(transaction_data, sort_keys=True).encode()
            public_key_hex = self.get_public_key(sender)
            vk = VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
            return vk.verify(signature, transaction_json)
        except Exception as e:
            print("Verification failed:", str(e))
            return False

    def get_public_key(self, user_key):
        for data_dict in [self.Identity_dict, self.Identity_admin, self.Identity_contestants]:
            for key, user_list in data_dict.items():
                for user_data in user_list:
                    if user_data['public_key'] == user_key:
                        return user_data['public_key']
        return None

    def get_balance(self, user_key):
        for data_dict in [self.Identity_dict, self.Identity_admin, self.Identity_contestants]:
            for key, user_list in data_dict.items():
                for user_data in user_list:
                    if user_data['public_key'] == user_key:
                        if "vot" in user_data:
                            return user_data["vot"]
        print("Get balance error")
        return None

    def decrease_balance(self, user_key, amount):
        for data_dict in [self.Identity_dict, self.Identity_admin, self.Identity_contestants]:
            for key, user_list in data_dict.items():
                for user_data in user_list:
                    if user_data['public_key'] == user_key:
                        if "vot" in user_data:
                            user_data["vot"] -= amount
                            return
        print("Decrease balance error: no 'vot' field found")

    def increase_balance(self, user_key, amount):
        for data_dict in [self.Identity_dict, self.Identity_admin, self.Identity_contestants]:
            for key, user_list in data_dict.items():
                for user_data in user_list:
                    if user_data['public_key'] == user_key:
                        if "vot" in user_data:
                            user_data["vot"] += amount
                        else:
                            user_data["vot"] = amount
                        return
        print("Increase balance error: no 'vot' field found")

    def get_leaf_values(self):
        leaf_values = []
        for key, value in self.Users.items():
            leaf_values.append(key)
        return leaf_values

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        leaf_values = self.get_leaf_values()

        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            for leaf_value in leaf_values:
                hash_operation += str(leaf_value)
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def hash_password(password):
        hashed_bytes = hashlib.sha256(password.encode('utf-8')).digest()
        hashed_password = base64.b64encode(hashed_bytes).decode('utf-8')
        return hashed_password

    def check_password(password, hashed_password):
        expected_hash = hashlib.sha256(password.encode('utf-8')).digest()
        print(expected_hash)
        return hashed_password == base64.b64encode(expected_hash).decode('utf-8')

    def generateAddress(private_key):
        public_key = hashlib.sha256(private_key.encode()).hexdigest()
        return public_key

    def generatePrivateKey():
        private_key = hashlib.sha256(os.urandom(2048)).hexdigest()
        return private_key

   