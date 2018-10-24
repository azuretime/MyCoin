from blockchain import *
from block import *
from merkletree import MerkleTree
import time
import socket
from multiprocessing import Process, Queue
from Miner import Miner

def server(q3,q4,q5):
    print("==================Server starts======================")
    UDP_IP = "localhost"
    UDP_PORT = 1357
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        msg, addr = sock.recvfrom(4096) # buffer size
        js = json.loads(msg)
        if js[0] == '0':
            print("=================Block received===================")
            print(js[1])
            blk = Block.from_json(js[1])
            q3.put(blk)

        if js[0] == '1':
            print("=================Transaction received===================")
            t = js[1]
            q4.put(t)

        if js[0] == '2':
            print("=================Coin request received================")
            receiver, amt = js[1],js[2]
            q5.put({receiver:amt})
            print(receiver, amt)


if __name__ == "__main__":
    miner = Miner('5ff904f38a0b1c1de04193668f7442c5146bd0c868eb2e31','b7e9e8c717bbfab299e6a4dbaacef166957aab1865a5762d4e22cc7de31057c99682651642e1bd6ad138c03e4f37f495')
    print('pubkey:', miner.pubkey)
    miner.port = ("localhost", 2346)
    q3 = Queue()
    q4 = Queue()
    q5 = Queue()
    p1 = Process(target=miner.mine_block, args=(q3,q4,q5))
    p2 = Process(target=server, args=(q3,q4,q5))
    p1.start()
    p2.start()





