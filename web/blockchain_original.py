# Module 1 - Create a Blockchain

# To be installed:
# Flask==0.12.2: pip install Flask==0.12.2
# Postman HTTP Client: https://www.getpostman.com/

# Importing the libraries
import datetime
import hashlib
import base64
import json
from flask import Flask, jsonify, request
import os

# Part 1 - Building a Blockchain

class Blockchain:
    Identity_dict= {}
    Identity_admin= {}
    Users= {}
    Identity_contestants = {}
    ToBeDetermined = {}
    Declined_users = {}

    def __init__(self):
        self.chain = []
        self.create_block(proof = 1, previous_hash = '0')
        self.balances = {}
        self.load_data("identity_data.json", "identity_admin_data.json","credentials_block.json", "contestants.json", "distribute_votes.json" )
        self.voting_start_date = None
        self.voting_end_date = None
        self.votes_distributed = None

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
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': []}
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def add_transaction(self, sender, receiver, amount):
        # Verificați dacă sender-ul are suficiente fonduri pentru a efectua tranzacția
        sender_balance = self.get_balance(sender)
        if sender_balance is None or sender_balance < amount:
            return False

        # Restul codului pentru adăugarea tranzacției în bloc
        if sender in self.Identity_admin:
            transaction = {
                'sender': sender,
                'receiver': receiver,
                'amount': amount
            }
        else:
                transaction = {
                'sender': Blockchain.generateAddress(sender),
                'receiver': receiver,
                'amount': amount
            }

        # Actualizați soldurile pentru sender și receiver
        self.decrease_balance(sender, amount)
        self.increase_balance(receiver, amount)

        self.chain[-1]['transactions'].append(transaction)
        return True


    def get_balance(self, user_key):
        k=0
        if user_key in self.Identity_dict:
            user_data = self.Identity_dict.get(user_key, [])
            k=1
        
        if user_key in self.Identity_admin:
            user_data = self.Identity_admin.get(user_key, [])
            k=1

        if user_key in self.Identity_contestants:
            user_data = self.Identity_contestants.get(user_key, [])
            k=1
        
        if k==0:
            print("Get balance error")
        
        # Verifică dacă cheia utilizatorului există și dacă are secțiunea "vot"
        if user_data and "vot" in user_data[0]:
            return user_data[0]["vot"]
        
    def decrease_balance(self, user_key, amount):
        k=0
        if user_key in self.Identity_dict:
            user_data = self.Identity_dict.get(user_key, [])
            k=1
        
        if user_key in self.Identity_admin:
            user_data = self.Identity_admin.get(user_key, [])
            k=1

        if user_key in self.Identity_contestants:
            user_data = self.Identity_contestants.get(user_key, [])
            k=1
        
        if k==0:
            print("Decrease balance error")


        # Verifică dacă cheia utilizatorului există și dacă are secțiunea "vot"
        if user_data and "vot" in user_data[0]:
            user_data[0]["vot"] -= amount
        else:
        # Dacă utilizatorul nu are secțiunea "vot", adaugă secțiunea și setează valoarea inițială
            user_data[0]["vot"] = amount


    def increase_balance(self, user_key, amount):
        # Crește soldul pentru un anumit utilizator
        if user_key in self.Identity_dict:
            user_data = self.Identity_dict.get(user_key, [])
        else:
            if user_key in self.Identity_admin:
                user_data = self.Identity_admin.get(user_key, [])
            else:
                if user_key in self.Identity_contestants:
                    user_data = self.Identity_contestants.get(user_key, [])
                else:
                    print("Increase balance error")

        # Verifică dacă cheia utilizatorului există și dacă are secțiunea "vot"
        if user_data and "vot" in user_data[0]:
            # Now, you can safely append the new value
            user_data[0]["vot"] += amount
        else:
        # Dacă utilizatorul nu are secțiunea "vot", adaugă secțiunea și setează valoarea inițială
            user_data[0]["vot"] = amount

    def get_leaf_values(self):
        # Returnează o listă de valori (chei) ale leaf-urilor din rețea
        leaf_values = []
        for key, value in self.Users.items():
            leaf_values.append(key)
        return leaf_values

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        leaf_values = self.get_leaf_values()  # Obțineți valorile leaf-urilor

        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()

            # Adăugăm la hash_operation valorile leaf-urilor
            for leaf_value in leaf_values:
                hash_operation += str(leaf_value)

            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
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
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
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

    def generateAddress(private_key):       #generation of the public and private addresses and they conversion in txt format
            public_key = hashlib.sha256(private_key.encode()).hexdigest()
            return public_key
    
    def generatePrivateKey():       #generation of the public and private addresses and they conversion in txt format
        private_key = hashlib.sha256(os.urandom(2048)).hexdigest()
        return private_key






# trebuie sa modific functile de populare
# sa modific functia de generate a cheilor