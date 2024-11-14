from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

key = RSA.generate(2048)
private_key = key
public_key = key.publickey()

# Export public and private keys (if needed)
private_pem = private_key.export_key()
public_pem = public_key.export_key()

# Load keys back from PEM (optional step for saving keys)
private_key = RSA.import_key(private_pem)
public_key = RSA.import_key(public_pem)

# Example message to sign
message = b'This is a secret message'

# Step 1: Create the SHA256 hash of the message
hash_message = SHA256.new(message)

# Step 2: Sign the hash using the private key
signature = pkcs1_15.new(private_key).sign(hash_message)

print("Signature:", signature)

# Step 3: Verify the signature using the public key
try:
    pkcs1_15.new(public_key).verify(hash_message, signature)
    print("The signature is valid. Message integrity and authenticity confirmed.")
except (ValueError, TypeError):
    print("The signature is invalid. Message integrity compromised.")
