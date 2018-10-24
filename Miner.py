import copy
from blockchain import *
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
        self.port = None


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
    def mine_block(self, q0, q1, q2):

        while True:
            TARGET = "0000" + "f"*60
            # Get the last block
            last_blk = self.blockchain.last_blk

            while not q0.empty():
                print("---------------there is a new block-------------")
                blk = q0.get()
                print("new block {}\n".format(blk.to_json))

                self.blockchain.add(blk)
                if blk.header['hash_of_previous_header'] == self.blockchain.last_blk.generate_header_hash():
                    self.blockchain.last_blk = blk
                else:
                    if len(self.blockchain.get_longest_chain(blk)) > len(self.blockchain.get_longest_chain(self.blockchain.last_blk)):
                         self.blockchain.last_blk = blk

            while not q1.empty():
            # validate and add txn to the pool
                trans_json = q1.get()
                #print(trans_json)
                self.add_transaction(trans_json)

            while not q2.empty():
            # validate and add txn to the pool
                msg = q2.get()
                receiver,amt = list(msg.keys())[0], list(msg.values())[0]
                self.create_transaction(receiver,int(amt),'')

            if self.transaction_pool == []:
                hash_of_previous_header = last_blk.generate_header_hash()
                tx0 = self.create_tx_0()
                root = MerkleTree([tx0.to_json()]).get_root()
                timestamp = int(round(time.time() * 1000))
                nonce = random.getrandbits(32)
                mined_blk = Block(hash_of_previous_header,root,timestamp,nonce,[tx0.to_json()])
                header_hash = mined_blk.generate_header_hash()
                while header_hash >= TARGET:
                    nonce = random.getrandbits(32)
                    mined_blk = Block(hash_of_previous_header,root,timestamp,nonce,[tx0.to_json()])
                    header_hash = mined_blk.generate_header_hash()
            else:

                print("Pool is not empty! ")
                hash_of_previous_header = last_blk.header['hash_of_previous_header']
                timestamp = int(round(time.time() * 1000))
                nonce = random.getrandbits(32)
                temp_txn = copy.deepcopy(self.transaction_pool)
                print("temp_txn:",temp_txn)
                self.transaction_pool = list(set(self.transaction_pool)-set(temp_txn))
                root = MerkleTree(temp_txn).get_root()
                mined_blk = Block(hash_of_previous_header,root,timestamp,nonce,temp_txn)
                header_hash = mined_blk.generate_header_hash()
                while header_hash >= TARGET:
                    nonce = random.getrandbits(32)
                    mined_blk = Block(hash_of_previous_header,root,timestamp,nonce,temp_txn)
                    header_hash = mined_blk.generate_header_hash()

            print("POW Done")
            block_json = mined_blk.to_json()

            # Add new block to the blockchain
            try:
                self.blockchain.add(mined_blk)
                self.blockchain.last_blk = mined_blk
                print("Successfully added block")
                time.sleep(3)
            except Exception as e:
                print("BLK_ADD_FAIL: {}".format(repr(e)))
            else:
                # Block successfully added to blockchain
                print("mined_blk:", mined_blk.to_json())
                self.compute_balance(mined_blk)
                print("Miner {0} balance: {1}".format(self.pubkey[:6], self.balance))
            self.broadcast_block(block_json)

    def broadcast_block(self,block_json):
        print("==================broadcast block starts======================")
        print(block_json)
        sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
        MESSAGE = ['0',block_json]
        try:
            sock.sendto(json.dumps(MESSAGE).encode(), self.port)
            #data, server = sock.recvform(4096)
            print("Data sent")
        finally:
            sock.close()

    # Create a new transaction
    def create_transaction(self, receiver, amount, comment):
        try:
            if amount > self.balance:
                raise Exception("Amount is higher than available balance.")
            print('Amount',amount, 'Balance',self.balance)
            receiver = ecdsa.VerifyingKey.from_string(bytes.fromhex(receiver))
            sender = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.pubkey))
            nonce = int(round(time.time() * 1000))
            trans = Transaction.new(sender, receiver,
                                    amount, self.privkey,
                                    nonce, comment)
        except Exception as e:
            print("TRANS_CREATION_FAIL: {}".format(repr(e)))
            return None
        else:
            #self.balance -= amount
            #print("New balance:", self.balance)
            trans_json = trans.to_json()
            self.add_transaction(trans_json)
            print('trans_json',trans_json)
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
            print("Trans_json is successfully added to pool")
        except ecdsa.BadSignatureError:
            print("TRANS_VERIFY_FAIL: Transaction verification failed.")


    # Recompute miner's balance using transactions in added block
    def compute_balance(self, block):
        for t_json in block.transactions:
            t = Transaction.from_json(t_json)
            if t.receiver == self.pubkey and t.sender == self.pubkey:
                self.balance += t.amt
                print("Miner receives 100 coins.")
            else:
                if t.receiver == self.pubkey:
                    print("Miner receives coins from client.")
                    self.balance += t.amt
                if t.sender == self.pubkey:
                    self.balance -= t.amt
                    print("Miner sold coins.")



def print_balance(miners):
    print("===================================================")
    for j in range(len(miners)):
        print("Miner {0} balance: {1}".format(j, miners[j].balance))
    print()

def server(q0,q1,q2):
    print("==================Server starts======================")
    UDP_IP = "localhost"
    UDP_PORT = 2346
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        msg, addr = sock.recvfrom(4096) # buffer size
        js = json.loads(msg)
        if js[0] == '0':
            print("=================Block received===================")
            blk = Block.from_json(js[1])
            q0.put(blk)
            print(js[1])

        if js[0] == '1':
            print("=================Transaction received===================")
            t = js[1]
            q1.put(t)

        if js[0] == '2':
            print("=================Coin request received================")
            receiver, amt = js[1],js[2]
            q2.put({receiver:amt})
            print(receiver, amt)



if __name__ == "__main__":
    miner = Miner('a87814292873a3050cb374cba745a900107ef365c01932b3','957bce29fc16ded351536e9adb7cf424fb7488fac0400ef0647164d96b756267ba2cc0dea63c2715c2cf20d06c72bc6e')
    print('pubkey:',miner.pubkey)
    miner.port = ("localhost", 1357)
    q0 = Queue()
    q1 = Queue()
    q2 = Queue()
    p1 = Process(target=miner.mine_block, args=(q0,q1,q2))
    p2 = Process(target=server, args=(q0,q1,q2))
    p1.start()
    p2.start()







