import ecdsa as ecdsa

from transaction import *
from blockchain import *
from block import *
from merkletree import MerkleTree
import time
import socket
from multiprocessing import Process, Queue

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
    def mine_block(self, q0,q1):

        while True:
            TARGET = "0000" + "f"*60
            # Resolve blockchain to get last block
            last_blk = self.blockchain.resolve()

            while not q0.empty():
                msg = q0.get()
                # validate and add block to blockchain
                #print(msg)

                temp_blockchain = self.blockchain
                self.blockchain.add(msg)
                if not self.blockchain.validate(msg):
                    self.blockchain = temp_blockchain
                #print('q0.empty()',q0.empty())

            while not q1.empty():
            # validate and add txn to the pool
                msg = q1.get()
                receiver,amt = list(msg.keys())[0], list(msg.values())[0]
                self.create_transaction(receiver,amt,'')

            if self.transaction_pool == [] and q1.empty():
                hash_of_previous_header = last_blk.generate_header_hash()
                tx0 = self.create_tx_0()
                root = MerkleTree([tx0.to_json()]).get_root()
                timestamp = int(round(time.time() * 1000))
                nonce = random.getrandbits(32)
                blk = Block(hash_of_previous_header,root,timestamp,nonce,[tx0.to_json()])
                header_hash = blk.generate_header_hash()
                while header_hash >= TARGET and q1.empty():
                    if self.transaction_pool == [] :
                        nonce = random.getrandbits(32)
                        blk = Block(hash_of_previous_header,root,timestamp,nonce,[tx0.to_json()])
                        header_hash = blk.generate_header_hash()
            else:
                if self.transaction_pool != []:
                    hash_of_previous_header = last_blk.header['hash_of_previous_header']
                    timestamp = int(round(time.time() * 1000))
                    nonce = random.getrandbits(32)
                    temp_txn = self.transaction_pool
                    self.transaction_pool = list(set(self.transaction_pool)-set(temp_txn))
                    root = MerkleTree(temp_txn).get_root()
                    blk = Block(hash_of_previous_header,root,timestamp,nonce,temp_txn)
                    header_hash = blk.generate_header_hash()
                    while header_hash >= TARGET:
                        nonce = random.getrandbits(32)
                        blk = Block(hash_of_previous_header,root,timestamp,nonce)
                        header_hash = blk.generate_header_hash()

            block_json = blk.to_json()
            #print(block_json)
            # Add new block to the blockchain
            try:
                self.blockchain.add(blk)
                time.sleep(3)
            except Exception as e:
                print("BLK_ADD_FAIL: {}".format(repr(e)))
            else:
                # Block successfully added to blockchain
                self.compute_balance(blk)
                print("Miner {0} balance: {1}".format(self.pubkey[:6], self.balance))
            self.broadcast_block(block_json)


    def broadcast_block(self,block_json):
        print("==================broadcast block starts======================")
        UDP_IP = "localhost"
        UDP_PORT = 4321
        sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
        MESSAGE = ['0',block_json]
        try:
            sock.sendto(json.dumps(MESSAGE).encode(), (UDP_IP, UDP_PORT))
            print("Data sent")
        finally:
            sock.close()

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

            #self.broadcast_transaction(trans_json)
            return trans


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
            if t.receiver == self.pubkey and t.sender == self.pubkey:
                self.balance += t.amt
            else:
                if t.receiver == self.pubkey:
                    self.balance += t.amt
                if t.sender == self.pubkey:
                    self.balance -= t.amt



def print_balance(miners):
    print("===================================================")
    for j in range(len(miners)):
        print("Miner {0} balance: {1}".format(j, miners[j].balance))
    print()

def server(q0,q1):
    print("==================Server starts======================")
    UDP_IP = "localhost"
    UDP_PORT = 12345
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        msg, addr = sock.recvfrom(4096) # buffer size is 1024 bytes
        js = json.loads(msg)
        if js[0] == '0':
            print("=================Block received===================")
            blk = Block.from_json(js[1])

            q0.put(blk)
        if js[0] == '2':
            receiver, amt = msg[1],msg[2]
            q1.put({receiver:amt})
            print(receiver, amt)



if __name__ == "__main__":
    miner = Miner.new()
    q3 = Queue()
    q4 = Queue()
    p1 = Process(target=miner.mine_block, args=(q3,q4))
    p2 = Process(target=server, args=(q3,q4))
    p1.start()
    p2.start()

    # num_miners = 5
    # miners = create_miner_network(num_miners)
    # for t in range(1):
    #     for i in range(0, len(miners)):
    #         print("Miner {0} starts mining".format(i))
    #         start = time.time()
    #         miners[i].mine_block()
    #         elapsed = time.time() - start
    #         print("Time to make new block: {}s".format(elapsed))
    #         print_balance(miners)


    # print(("Miner 0 is sending {0} transactions of amount {1} "
    #        "to random miners...").format(3, 5))
    # for i in range(3):
    #     index = random.randint(1, num_miners - 1)
    #     receiver=miners[index].pubkey
    #     miners[0].create_transaction(receiver=ecdsa.VerifyingKey.from_string(bytes.fromhex(receiver)),
    #                                  amount=5, comment="random")
    #     print_balance(miners)






