import time
import json
import random
import ecdsa
import socket
from transaction import Transaction


class spvclient:

    def __init__(self):
        privkey = ecdsa.SigningKey.generate()
        self.privkey = privkey.to_string().hex()
        self.pubkey = privkey.get_verifying_key().to_string().hex()
        self.transaction = []
        self.bc_header = []
        self.tx_proof = {}
        self.balance = 0


    def add_transcation(self,receiver, amt, cmt):
        sender = self.pubkey
        sender = ecdsa.VerifyingKey.from_string(bytes.fromhex(sender))
        receiver = receiver
        amount = amt
        comment = cmt
        privkey = self.privkey
        nonce = random.getrandbits(32)
        t = Transaction.new(sender, receiver, amount, privkey,nonce, comment)
        self.transaction.append(t.to_json())

    def send_transaction(self,addr):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.transaction.insert(0,'1')

        msg = self.transaction

        try:
            print("Transaction: ",msg)
            sock.sendto(json.dumps(msg).encode(), addr)

        finally:
            sock.close()


    def buy_coin_from_miner(self,addr,amt):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        msg = ['2', self.pubkey, str(amt)]
        print("The msg is ", msg)

        try:
            sock.sendto(json.dumps(msg).encode(), addr)

        finally:
            sock.close()


if __name__ == "__main__":

    c1 = spvclient()
    addr = ("localhost", 2346)
    c1.buy_coin_from_miner(addr,10)
    time.sleep(4)
    receiver = '957bce29fc16ded351536e9adb7cf424fb7488fac0400ef0647164d96b756267ba2cc0dea63c2715c2cf20d06c72bc6e' # run Miner and copy the pubkey here
    receiver = ecdsa.VerifyingKey.from_string(bytes.fromhex(receiver))
    c1.add_transcation(receiver, 20, "Send 20 to a Miner")
    print(c1.transaction)
    c1.send_transaction(addr)


