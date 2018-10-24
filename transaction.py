import ecdsa, json, time

class Transaction:
    def __init__(self, sender, receiver, amt, nonce, cmt="", sig=None):
        self.sender = sender
        self.receiver = receiver
        self.amt = amt
        self.cmt = cmt
        self.nonce = nonce
        self.sig = sig

    # Instantiates object from passed values
    @classmethod
    def new(cls, sender, receiver, amt, senderPk, nonce, cmt=""):
        sender = sender.to_string().hex()
        receiver = receiver.to_string().hex()
        t = cls(sender, receiver, amt, nonce, cmt)
        t.sign(senderPk)
        if t.validate():
            return t

    # Serializes object to JSON string
    def to_json(self):
        s = json.dumps({
            "sender": self.sender,
            "receiver": self.receiver,
            "amt": self.amt,
            "cmt": self.cmt,
            "nonce": self.nonce,
            "sig": self.sig
        })
        return s

    # Instantiates/Deserializes object from JSON string
    @classmethod
    def from_json(cls, j):
        jstr  = json.loads(j)
        for item in jstr.keys():
            if item not in ['sender','receiver','amt','nonce','sig','cmt']:
                raise Exception("Invalid key "+ item +" is found in transaction JSON")
        t = cls(
            sender=jstr["sender"],
            receiver=jstr["receiver"],
            amt=jstr["amt"],
            nonce=jstr["nonce"],
            sig=jstr["sig"],
            cmt=jstr["cmt"]
        )
        if t.validate():
            return t


    # Sign object with private key passed
    # Can be called within new()
    def sign(self, privkey):
        privkey = ecdsa.SigningKey.from_string(bytes.fromhex(privkey))
        self.sig = privkey.sign(self.to_json().encode()).hex()

    # Verify sig
    def verify(self):
        # Remove sig before verifying
        sig = self.sig
        self.sig = None
        ecdsa_pubkey = ecdsa.VerifyingKey.from_string(bytes.fromhex(self.sender))
        result = ecdsa_pubkey.verify(bytes.fromhex(sig), self.to_json().encode())
        self.sig = sig
        return result

    # Validate transaction correctness.
    # Can be called within from_json()
    def validate(self):
        for s in ['self.sender','self.receiver','self.sig','self.cmt']:
            if not isinstance(eval(s), str):
                raise Exception(s.replace('self.','')+" is not a string.")
        if len(self.sender)  != 96 or len(self.receiver)  != 96:
            raise Exception("Public key string length is invalid.")
        for i in ['self.amt','self.nonce']:
            if not isinstance(eval(i), int):
                raise Exception(i.replace('self.','')+" is not an integer.")
        if self.amt<= 0:
            raise Exception('Transaction amount must be greater than 0.')
        if len(self.sig) != 96:
            raise Exception('Signature length is invalid.')
        return True

    # Check whether transactions are the same
    def __eq__(self, other):
        return self.to_json() == other.to_json()

    # String method for printing
    def __str__(self):
        string = "Transaction Information\n"
        string += "============================\n"
        string += "Sender: {}\n".format(self.sender)
        string += "Receiver: {}\n".format(self.receiver)
        string += "amt: {}\n".format(self.amt)
        temp = "N/A" if self.cmt == "" else self.cmt
        string += "cmt: {}\n".format(temp)
        string += "Nonce: {}\n".format(self.nonce)
        temp = "N/A" if self.sig == None else self.sig
        string += "sig: {}".format(temp)
        return string


if __name__ == "__main__":
    # Private Keys
    senderSk = ecdsa.SigningKey.generate()
    receiverSk = ecdsa.SigningKey.generate()
    senderPk = senderSk.to_string().hex()

    # Public Keys
    sender = senderSk.get_verifying_key()
    receiver = receiverSk.get_verifying_key()

    amt = 100
    cmt = '1st transaction'
    nonce = int(round(time.time() * 1000)) # integer milliseconds
    t = Transaction.new(sender, receiver, amt, senderPk,
                        nonce, cmt)
    t2 = Transaction.from_json(t.to_json())
    print(t)
    assert t2.verify()
    assert t == t2
