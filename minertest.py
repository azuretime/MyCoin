from transaction import *
from blockchain import *
from block import *
from merkletree import MerkleTree
import time
import socket
import itertools

class Miner:

    def __init__(self, privkey, pubkey):
        self.privkey = privkey
        self.pubkey = pubkey
        self.balance = 0
        self.blockchain = Blockchain.new()
        self.transaction_pool = []
        self.peers = []

    @classmethod
    def new(cls):
        sk = ecdsa.SigningKey.generate()
        vk = sk.get_verifying_key()
        privkey = sk.to_string().hex()
        pubkey = vk.to_string().hex()
        return cls(privkey, pubkey)

    def create_tx_0(self):
        # Private Keys
        senderPk = self.privkey
        # Public Keys
        sender = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.pubkey))
        amt = 100
        cmt = '1st transaction'
        nonce = int(round(time.time() * 1000)) # integer milliseconds
        return Transaction.new(sender, sender, amt, senderPk,
                        nonce, cmt)

    # Mine a new block
    def mine_block(self):
        TARGET = "0000" + "f"*60
        # Resolve blockchain to get last block
        last_blk = self.blockchain.resolve()
        time.sleep(1.8)
        if self.transaction_pool == []:
            hash_of_previous_header = last_blk.generate_header_hash()
            tx0 = self.create_tx_0()
            root = MerkleTree([tx0.to_json()]).get_root()
            timestamp = int(round(time.time() * 1000))
            nonce = random.getrandbits(32)
            blk = Block(hash_of_previous_header,root,timestamp,nonce,[tx0.to_json()])
            header_hash = blk.generate_header_hash()
            while header_hash >= TARGET:
                if self.transaction_pool == []:
                    timestamp = int(round(time.time() * 1000))
                    nonce = random.getrandbits(32)
                    blk = Block(hash_of_previous_header,root,timestamp,nonce,[tx0.to_json()])
                    header_hash = blk.generate_header_hash()
        else:
            hash_of_previous_header = last_blk.header['hash_of_previous_header']
            timestamp = int(round(time.time() * 1000))
            nonce = random.getrandbits(32)
            temp_txn = self.transaction_pool
            root = MerkleTree(temp_txn).get_root()
            blk = Block(hash_of_previous_header,root,timestamp,nonce,temp_txn)
            header_hash = blk.generate_header_hash()
            while header_hash >= TARGET:
                timestamp = int(round(time.time() * 1000))
                nonce = random.getrandbits(32)
                blk = Block(hash_of_previous_header,root,timestamp,nonce)
                header_hash = blk.generate_header_hash()

        block_json = blk.to_json()

        #print('Json:',block_json)

        # Add new block to the blockchain
        try:
            self.blockchain.add(blk)
        except Exception as e:
            print("BLK_ADD_FAIL: {}".format(repr(e)))
        else:
            # Block successfully added to blockchain
            for t_json in blk.transactions:
                t = Transaction.from_json(t_json)
                if t.receiver == self.pubkey and t.sender == self.pubkey:
                    self.balance += t.amt
                else:
                    if t.receiver == self.pubkey:
                        self.balance += t.amt
                    if t.sender == self.pubkey:
                        self.balance -= t.amt
        self.broadcast_block(block_json)
        #return blk

    # Broadcast the block to the network
    def broadcast_block(self, block_json):
        # Assume that peers are all nodes in the network
        # (of course, not practical IRL since its not scalable)
        for p in self.peers:
            p.add_block(block_json)

    # Create a new transaction
    def create_transaction(self, receiver, amount, comment):
        try:
            if amount > self.balance:
                raise Exception("Amount is higher than available balance.")
            sender = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.pubkey))
            nonce = int(round(time.time() * 1000))
            trans = Transaction.new(sender, receiver,
                                    amount, self.privkey,
                                    nonce, comment)
        except Exception as e:
            print("TRANS_CREATION_FAIL: {}".format(repr(e)))
            return None
        else:
            self.balance -= amount
            trans_json = trans.to_json()
            self.add_transaction(trans_json)
            self.broadcast_transaction(trans_json)
            return trans

    # Broadcast the transaction to the network
    def broadcast_transaction(self, trans_json):
        # Assume that peers are all nodes in the network
        # (of course, not practical IRL since its not scalable)
        for p in self.peers:
            p.add_transaction(trans_json)

    # Add transaction to the pool of transactions
    def add_transaction(self, trans_json):
        if trans_json in self.transaction_pool:
            print("TRANS_ADD_FAIL: Transaction already exist in pool.")
            return
        trans = Transaction.from_json(trans_json)
        try:
            trans.verify()
            self.transaction_pool.append(trans_json)
        except ecdsa.BadSignatureError:
            print("TRANS_VERIFY_FAIL: Transaction verification failed.")

    # Add miner to peer list
    def add_peer(self, miner):
        self.peers.append(miner)

    # Add new block to the blockchain
    def add_block(self, block_json):
        block = Block.from_json(block_json)
        try:
            self.blockchain.add(block)
        except Exception as e:
            print("BLK_ADD_FAIL: {}".format(repr(e)))
        else:
            # Block successfully added to blockchain
            self.compute_balance(block)

    # Recompute miner's balance using transactions in added block
    def compute_balance(self, block):
        for t_json in block.transactions:
            t = Transaction.from_json(t_json)
            if t.receiver == self.pubkey:
                self.balance += t.amt
            if t.sender == self.pubkey:
                self.balance -= t.amt

def create_miner_network(n):
    if n < 2:
        raise Exception("At least 2 miners are needed.")
    miners = [Miner.new() for _ in range(n)]
    for m1,m2 in itertools.permutations(miners,2):
        m1.add_peer(m2)
    return miners


def print_balance(miners):
    print("===================================================")
    for j in range(len(miners)):
        print("Miner {0} balance: {1}".format(j, miners[j].balance))
    print()


if __name__ == "__main__":
    num_miners = 5
    miners = create_miner_network(num_miners)
    for t in range(5):
        for i in range(0, len(miners)):
            print("Miner {0} starts mining".format(i))
            start = time.time()
            miners[i].mine_block()
            elapsed = time.time() - start
            print("Time to make new block: {}s".format(elapsed))
            print_balance(miners)


    # print(("Miner 0 is sending {0} transactions of amount {1} "
    #        "to random miners...").format(3, 5))
    # for i in range(3):
    #     index = random.randint(1, num_miners - 1)
    #     receiver=miners[index].pubkey
    #     miners[0].create_transaction(receiver=ecdsa.VerifyingKey.from_string(bytes.fromhex(receiver)),
    #                                  amount=5, comment="random")
    #     print_balance(miners)


