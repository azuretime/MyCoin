import json,hashlib

class Block:
    def __init__(self, hash_of_previous_header = None,root = None,
                    timestamp = None,nonce= None, transactions = None):

        self.transactions = transactions
        self.header = {
            'hash_of_previous_header': hash_of_previous_header,
            'root': root, #MerkleTree(transactions).get_root(),
            'timestamp': timestamp, #int(round(time.time() * 1000)), integer milliseconds
            'nonce': nonce # random.getrandbits(32)
        }

    def generate_header_hash(self):
        return hashlib.sha256(json.dumps(self.header).encode()).hexdigest()

    def to_json(self):
        return json.dumps({
            "header": self.header,
            "transactions": self.transactions
        })

    @classmethod
    def from_json(cls, json_str):
        j = json.loads(json_str)
        fields = ["header", "transactions"]
        if not all(elem in j.keys() for elem in fields):
            raise Exception("Block JSON string is invalid.")
        header_fields = ["hash_of_previous_header", "root", "timestamp", "nonce"]
        if not all(elem in j["header"].keys() for elem in header_fields):
            raise Exception("Block JSON header is invalid.")
        block = cls(j["header"]["hash_of_previous_header"],j["header"]['root'],
         j["header"]['timestamp'], j["header"]['nonce'], j["transactions"])
        return block



