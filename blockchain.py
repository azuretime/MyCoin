from merkletree import MerkleTree
import time, hashlib, json, random
from block import Block
from transaction import *

class Blockchain:

    def __init__(self):
        self.last_blk = None
        self.block_dict = {}

    # Instantiates object from passed values
    @classmethod
    def new(cls):
        blockchain = cls()
        genesis_block = Block('0'*64)
        blockchain.last_blk= genesis_block
        blockchain.block_dict[genesis_block.generate_header_hash()] = genesis_block
        return blockchain

    def add(self, block):
        if not self.validate(block):
            raise Exception("invalid block.")
        self.block_dict[block.generate_header_hash()] = block

    # Serializes object to JSON string
    def to_json(self):
        s = json.dumps({
            "last_blk": self.last_blk,
            "block_dict": self.block_dict
        })
        return s

    def resolve(self):
    # return the latest block of the longest chain
        return self.last_blk

    def get_longest_chain(self, block):
        chain = [block]
        temp_block = block
        previous_header = temp_block.header.get('hash_of_previous_header')
        while previous_header != '0'*64:
            chain.insert(0,self.block_dict.get(previous_header))
            temp_block = self.block_dict.get(previous_header)
            previous_header = temp_block.header.get('hash_of_previous_header')
        return chain

    def validate(self, block):
        # validate hash of header, previous_header
        TARGET = "0000" + "f"*60
        hash_target = hashlib.sha256(json.dumps(block.header).encode()).hexdigest()
        hash_header_validation = hash_target < TARGET
        previous_header_validation =  block.header['hash_of_previous_header'] in self.block_dict

        print('hash_header_validation',hash_header_validation)
        print('previous_header_validation',previous_header_validation)
        return hash_header_validation and previous_header_validation

#
# if __name__ == "__main__":
#     bc = Blockchain.new()
#     last_blk = bc.resolve()
#     print(last_blk.to_json())
#
#     TARGET = "0000" + "f"*60
#
#     tx = create_transactions(3)
#
#     hash_of_previous_header = last_blk.generate_header_hash()
#     root = MerkleTree(tx).get_root()
#     timestamp = int(round(time.time() * 1000))
#     nonce = random.getrandbits(32)
#     blk = Block(hash_of_previous_header,root,timestamp,nonce,tx)
#     header_hash = blk.generate_header_hash()
#     while header_hash >= TARGET:
#         timestamp = int(round(time.time() * 1000))
#         nonce = random.getrandbits(32)
#         blk = Block(hash_of_previous_header,root,timestamp,nonce,tx)
#         header_hash = blk.generate_header_hash()
#
#     bc.add(blk)
#     print(bc.validate(blk))
