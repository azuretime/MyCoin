from merkletree import MerkleTree
import time, hashlib, json, random
from block import Block
from transaction import *


class Blockchain:
    def __init__(self, blocks = []):
        self.blocks = blocks
        self.block_dict = {}

    # Instantiates object from passed values
    @classmethod
    def new(cls):
        blockchain = cls([])
        genesis_block = Block('000')
        blockchain.blocks.append(genesis_block)
        blockchain.block_dict[genesis_block.generate_header_hash()] = 1
        return blockchain

    def add(self, block):
        # if not self.validate(block):
        #     raise Exception("invalid block.")

        self.blocks.append(block)
        previous_block = self.block_dict.pop(block.header['hash_of_previous_header'], None)
        if previous_block:
            # the previous block is the tail of the blockchain, add itself in and increment length
            self.block_dict[block.generate_header_hash()] = previous_block + 1
        else:
            # the previous block is not the tail, so the current block is a fork.
            # calculate the length by traversing backwards.
            count = 1
            previous_header = block.header['hash_of_previous_header']
            while previous_header:
                for temp_block in reversed(self.blocks):
                # find the previous block
                    if temp_block.generate_header_hash() == previous_header:
                        count += 1
                        previous_header = temp_block.header['hash_of_previous_header']

            self.block_dict[block.generate_header_hash()] = count


    # Serializes object to JSON string
    def to_json(self):
        s = json.dumps({
            "blocks": self.blocks.to_string().hex()
        })
        return s

    # Instantiates/Deserializes object from JSON string
    @classmethod
    def from_json(cls, j):
        jstr  = json.loads(j)
        return cls.new(jstr['blocks'])

    def resolve(self):
    # return the latest block of the longest chain
        longest_chain = max(self.block_dict, key=self.block_dict.get)
        for block in self.blocks:
            if block.generate_header_hash() == longest_chain:
                self.block_dict = { longest_chain: self.block_dict[longest_chain] }
                return block

    def get_bc_headers(self):
        block = self.resolve()
        previous_header = block.header['hash_of_previous_header']
        bc_headers = [block.header.generate_header_hash()]
        while previous_header:
            for temp_block in reversed(self.blocks):
            # find the previous block
                if temp_block.generate_header_hash() == previous_header:
                  bc_headers.insert(0,previous_header)
                  previous_header = temp_block.header['hash_of_previous_header']
        return bc_headers

    def validate(self, block):
        # validate hash of header, previous_header
        TARGET = "0000" + "f"*60
        hash_target = hashlib.sha256(json.dumps(block.header).encode()).hexdigest()
        hash_header_validation = hash_target < TARGET
        previous_header_validation = False

        for temp_block in reversed(self.blocks):
            if block.header['hash_of_previous_header'] == temp_block.generate_header_hash():
                previous_header_validation = True and hash_target == block.generate_header_hash()
                break
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
