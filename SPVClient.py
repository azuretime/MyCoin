import hashlib
import json
import time
import ecdsa
import socket
from transaction import Transaction


class spvclient:

    def __init__(self):
        self.privkey = ecdsa.keys.SigningKey.to_string().hex()
        self.pubkey = ecdsa.keys.VerifyingKey.to_string().hex()
        self.transaction = []
        self.history = {}
        self.bc_header = []
        self.tx_proof = {}
        self.balance = 0
        self.ID = 0

    def add_transcation(self,tmsg): # tmsg = [receiver, amt, cmt]
        sender = self.pubkey
        receiver = tmsg[0]
        amount = int(tmsg[1])
        comment = tmsg[2]
        privkey = ecdsa.SigningKey.from_string(bytes.fromhex(self.privkey))
        t = Transaction.new(sender, receiver, amount, privkey, comment)
        self.transaction.append(t.to_json())

    def send_transaction(self,addr):
        # store the transaction to list
        self.history[str(self.ID)] = self.transaction
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = addr
        self.transaction.insert(0,'0')
        msg = self.transaction

        try:
            print(msg)
            sent = sock.sendto(json.dumps(msg).encode(), addr)
            data, addr = sock.recvfrom(1024)
            if data == "received":
                print("Miner have received")
                self.ID += 1
                self.transaction = []
            else:
                print("There is an error in Transaction: ", data)
        finally:
            sock.close()

    # get proof and the particular tx ( do it later )
    # give pk and miner return me pair of proof with tx in [[]]

    def buy_coin(self,addr,amt):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        addr = addr
        msg = ['2', self.pubkey, str(amt)]
        # print("The msg is ", msg.encode())

        try:
            sock.sendto(json.dumps(msg).encode(), addr)
            data, server = sock.recvfrom(4096)
            print("New balance of client: {}".format(data.decode()))

        finally:
            sock.close()

    def double_hash(self,node1, node2):
        return hashlib.sha256((node1 + node2).encode()).hexdigest()

    def get_tx_set(self,addr):
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        addr = addr
        msg = ['1', self.vk]
        try:
            sent = sock.sendto(json.dumps(msg).encode(), addr)

            data,server = sock.recvfrom(4096)
            print("Receive tx_set !")
            self.bc_header, self.tx_proof = json.loads(data)
        finally:
            sock.close()

    def proof(self):
        count = 0
        for tx in self.tx_proof:
            print(tx)
            test_val = hashlib.sha256(tx.encode()).hexdigest()
            for i in range(0, len(self.tx_proof[tx])):
                if self.tx_proof[tx][i][1] == 'l':
                    test_val = self.double_hash(self.tx_proof[tx][i][0], test_val)
                else:
                    test_val = self.double_hash(test_val, self.tx_proof[tx][i][0])

            for s in self.bc_header:
                if test_val == s[1]:
                    count += 1
        if count == len(self.tx_proof):
            print("All transactions are correct")
            return True
        else:
            print("The transactions are not correct")
            return False


if __name__ == "__main__":

    u1 = spvclient()  # m1's user
    # u2 = spvclient()  # m2's user
    # u3 = spvclient()  # m3's user



    # u1.set_keys('b5ed3a3c7450fc563431b7d55a18cda34f98ec5a47400531',
    #             '1905d27c355517d8522bdfa7d77c74ab3c64386e4c39bbee6e978c075941cd8937a62532e6ca9b1664705b6c55e4e89e')
    addr = ("127.0.0.1", 5005)
    # u1.buy_coin(addr, 100)
    # t1 = ['4e5a6ad6bf4f64f964d22e7ba059f71358c01b1688a33c3b6b5d6929ca8dc4cd68a115afff480c1858f6c42d3770a46d',50,"1"]
    # t2 = ['9ec3ae4d79ce1324441db8fa588c3beb4be14e982f319b5ec0bc05c1adf04483ba86b61ecd84130ca69296bdf9d9b478',15,"2"]
    # u1.add_transcation(t1)
    # u1.add_transcation(t2)
    # u1.send_transaction(addr)

    # u1.get_tx_set(addr)
    # u1.proof()

    # time.sleep(5)
    # u1.get_tx_set(addr)
    # u1.proof()
