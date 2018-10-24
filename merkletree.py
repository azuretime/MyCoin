
import hashlib,random
from collections import OrderedDict


class MerkleTree():
    def __init__(self,listoftransaction=[]):
        self.listoftransaction = listoftransaction
        self.past_transaction = []
        self.build()

    def add(self,ls):
        # Add entries to tree
        self.listoftransaction.extend(ls)


    def build(self):
        # Build tree computing new root
        listoftransaction = self.listoftransaction
        temp_transaction = []
        past_transaction = OrderedDict()
        # genesis block
        if len(listoftransaction) == 0:
            current_hash = hashlib.sha256(''.encode('utf-8'))
            past_transaction[''] = current_hash.hexdigest()
            self.past_transaction.append(past_transaction)
        else:
            # Loop until the list finishes
            for index in range(0,len(listoftransaction),2):
                # Get the most left element
                current = listoftransaction[index]
                # If there is still index left get the right of the left most element
                if index+1 != len(listoftransaction):
                    current_right = listoftransaction[index+1]
                # If we reached the limit of the list then make a empty string
                else:
                    current_right = ''


                # Apply the Hash 256 function to the current values
                current_hash = hashlib.sha256(current.encode('utf-8'))
                current_right_hash = hashlib.sha256(current_right.encode('utf-8'))
                # Add the Transaction to the dictionary
                past_transaction[current] = current_hash.hexdigest()
                past_transaction[current_right] = current_right_hash.hexdigest()

                # Create the new list of transaction
                temp_transaction.append(current_hash.hexdigest() + current_right_hash.hexdigest())


              # Update the variables and rerun the function again
            if len(listoftransaction) != 1:
                self.listoftransaction = temp_transaction
                self.past_transaction.append(past_transaction)
                # Call the function repeatly again and again until we get the root
                self.build()
            else:
                self.past_transaction.append(past_transaction)
                #print(self.past_transaction)
                #print(len(self.past_transaction))

    def get_proof(self,entry):
        # Get membership proof for entry
        proof = []
        leaves = list(self.past_transaction[0])
        if entry not in leaves:
            return "Entry not found"
        idx = leaves.index(entry)
        #print(idx)
        height = 0
        for j in range(0,len(self.past_transaction)-1):
            if idx%2 == 0:
                proof.append((list(self.past_transaction[j].items())[idx+1][1], "right"))
            else:
                proof.append((list(self.past_transaction[j].items())[idx-1][1], "left"))
            idx = int(idx/2)
            #print(idx)
        return proof


    def get_root(self):
        # Return the current root
        return list(self.past_transaction[-1].items())[0][1]


def verify_proof(entry, proof, root):
    # Verifies proof for entry and given root. Returns boolean.
    temp = hashlib.sha256(entry.encode('utf-8')).hexdigest()
    for h, d in proof:
        if d == "right":
            inp = temp + h
        elif d == "left":
            inp = h + temp
        else:
            raise Exception("Invalid direction in proofs.")
        temp = hashlib.sha256(inp.encode('utf-8')).hexdigest()
    return temp == root

if __name__ == "__main__":

    print("Generating transactions...")
    transactions = random.randint(10,11)
    items = [str(random.randint(0,1000000)) for i in range(transactions)]
    tree = MerkleTree(items)
    print("Computing root...")
    root = tree.get_root()
    print("Root: " + root)
    print("Computing proof for random entry...")
    for i in range(1,11):
        print("Test",i)
        entry = items[random.randint(0, len(items)-1)]
        proof = tree.get_proof(entry)
        print("Proof: " + str(proof))
        ver = verify_proof(entry, proof, root)
        print("Verify: " + ("Success" if ver else "Failure"))
