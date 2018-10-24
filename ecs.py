import ecdsa
sk = ecdsa.SigningKey.generate()
vk = sk.get_verifying_key()
privkey = sk.to_string().hex()
pubkey = vk.to_string().hex()
print(pubkey)
print(privkey)
