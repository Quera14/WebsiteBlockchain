import datetime
import json
import time

import hashlib
from Crypto.Hash import keccak
from skein import skein256

import random

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

def get_hash(hash_type, data):
    hash_operation = ''
    if hash_type == 'sha256':
        hash_operation = hashlib.sha256(data).hexdigest()
    elif hash_type == 'keccak':
        keccak_hash = keccak.new(digest_bits=256)
        keccak_hash.update(data)
        hash_operation = keccak_hash.hexdigest()
    elif hash_type == 'skein':
        skein = skein256()
        skein.update(data)
        hash_operation = skein.hexdigest()
    return hash_operation

class Blockchain:
    def __init__(self, hash_type):
        self.chain = []
        self.hash_type = hash_type
        proof, curr_hash = self.proof_of_work(0)
        block = self.create_block(proof, '0000000000000000000000000000000000000000000000000000000000000000', data='')
        self.chain[0]["curr_hash"] = curr_hash


    def create_block(self, proof, prev_hash, data):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'data': data,
                 'proof': proof,
                 'prev_hash': prev_hash}
        self.chain.append(block)
        return block

    def get_prev_block(self):
        return self.chain[-1]

    def proof_of_work(self, prev_proof, data = ''):
        new_proof = 1
        hash_operation = ""
        check_proof = False
        while check_proof is False:
            hash_operation = get_hash(self.hash_type, (str(new_proof**2 - prev_proof**2)+data).encode())
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof, hash_operation

    def mine_block(self, data, index):
        block = self.chain[index-1]
        block['data'] = data
        prev_proof = 0
        if index >= 2:
            prev_proof = self.chain[index-2]['proof']
        else:
            prev_proof = 0
        proof, hash = self.proof_of_work(prev_proof, data)
        block['proof'] = proof
        block['curr_hash'] = hash
        self.chain[index-1] = block
        return block

    def hash (self, block):
        encoded_block = json.dumps(block, sort_keys= True).encode()
        return get_hash(self.hash_type, encoded_block)

    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = get_hash(self.hash_type, str(proof**2 - prev_proof**2).encode())
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True


blockchain = {
    "sha256": Blockchain("sha256"),
    "keccak": Blockchain("keccak"),
    "skein": Blockchain("skein"),
}


def mine_block(blockchain, data):
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block ['proof']
    proof, curr_hash = blockchain.proof_of_work(prev_proof)
    prev_hash = prev_block["curr_hash"]
    block = blockchain.create_block(proof, prev_hash, data)
    blockchain.chain[len(blockchain.chain) - 1]["curr_hash"] = curr_hash
    response = {'message': 'Congrats, you just mined a block!',
                'index': block['index'],
                'data': block['data'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash']}
    return (response)

def get_chain(blockchain):
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return (response)

def get_blocks(hash_type):
    blockchain = Blockchain(hash_type)

    for i in range(COUNT):
        start_time = time.time()

        paragraphs_length = random.randrange(3, 5)
        block = mine_block(blockchain, ''.join(fake.paragraphs(paragraphs_length)))


    res = get_chain(blockchain)

    return res


for key, val in blockchain.items():
    for i in range(4):
        mine_block(val, '')
    chain = get_chain(val)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/blockchain/{algo}")
def api_get_chain(algo: str):
    chain = blockchain[algo]
    data = get_chain(chain)
    return data

class BlockData(BaseModel):
    data: str

@app.post("/blockchain/{algo}/mine/{index}")
def api_mine_block_at_idx(algo: str, index: int, data: BlockData):
    chain = blockchain[algo]
    res = chain.mine_block(data.data, index)
    return res
