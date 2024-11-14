from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes
import random

class PCA:
    """
    Pseudonym Certification Authority (PCA) responsible for issuing and signing certified pseudonyms.
    """
    def __init__(self):
        self.key = RSA.generate(2048)  # PCA's RSA key for signing
        self.n = self.key.n  # RSA modulus
        self.e = self.key.e  # RSA public exponent
        self.issued_certificates = {}  # Track issued pseudonyms to avoid duplicates

    def sign_blinded_pseudonym(self, blinded_pseudonym):
        """
        Sign a blinded pseudonym for a user.
        """
        signed_blinded_pseudonym = pow(blinded_pseudonym, self.key.d, self.n)
        return signed_blinded_pseudonym

    def issue_pseudonym(self, user, time_slot):
        """
        Issue a certified pseudonym to a user for a specified time slot.
        """
        if (user.real_identity, time_slot) in self.issued_certificates:
            raise Exception("Pseudonym for this user and time slot already issued.")
        
        pseudonym = user.generate_pseudonym(time_slot)
        blinded_pseudonym = user.blind_pseudonym(pseudonym)
        signed_blinded_pseudonym = self.sign_blinded_pseudonym(blinded_pseudonym)
        user.receive_signed_pseudonym(signed_blinded_pseudonym)

        # Register issued pseudonym
        self.issued_certificates[(user.real_identity, time_slot)] = pseudonym
        print(f"Pseudonym for user {user.real_identity} issued for time slot {time_slot}.")

    def verify_pseudonym(self, pseudonym, signed_pseudonym):
        """
        Verify the signed pseudonym to check if it is valid.
        """
        # Check if the signed pseudonym corresponds to the original pseudonym
        is_valid = pow(signed_pseudonym, self.e, self.n) == pseudonym
        return is_valid


class User:
    """
    User class representing a network participant with a real identity and pseudonyms.
    """
    def __init__(self, real_identity, pca):
        self.real_identity = real_identity
        self.pca = pca
        self.rsa_key = RSA.generate(2048)  # User's RSA key for encryption/decryption
        self.n = pca.n  # PCA's modulus
        self.e = pca.e  # PCA's public exponent
        self.pseudonyms = {}  # Store pseudonyms per time slot
        self.signed_pseudonym = None

    def generate_pseudonym(self, time_slot):
        """
        Generate a unique pseudonym for a specific time slot.
        """
        pseudonym = f"pseudonym_{self.real_identity}_{time_slot}"
        pseudonym_number = bytes_to_long(pseudonym.encode())
        self.pseudonyms[time_slot] = pseudonym_number
        return pseudonym_number

    def blind_pseudonym(self, pseudonym):
        """
        Blind the pseudonym using a random blinding factor.
        """
        while True:
            self.r = random.randrange(1, self.n)
            if self.r % self.n != 0:
                break
        self.r_inv = pow(self.r, -1, self.n)  # modular inverse of r mod n
        blinded_pseudonym = (pseudonym * pow(self.r, self.e, self.n)) % self.n
        return blinded_pseudonym

    def receive_signed_pseudonym(self, signed_blinded_pseudonym):
        """
        Unblind the signed pseudonym received from the PCA.
        """
        # Unblind the pseudonym to obtain the signature on the original pseudonym
        self.signed_pseudonym = (signed_blinded_pseudonym * self.r_inv) % self.n
        print(f"User {self.real_identity} received signed pseudonym.")

    def send_for_verification(self, time_slot):
        """
        Send pseudonym and signed pseudonym to PCA for verification.
        """
        pseudonym = self.pseudonyms[time_slot]
        return self.pca.verify_pseudonym(pseudonym, self.signed_pseudonym)


# Example usage:
# Initialize PCA (Pseudonym Certification Authority)
pca = PCA()

# Create a user with a unique real identity and link to the PCA


user = User("UserA_RealID", pca)

# Issue a pseudonym for a specific time slot
time_slot = 4
pca.issue_pseudonym(user, time_slot)


# User requests verification of their pseudonym for the specified time slot
if user.send_for_verification(time_slot):
    print("The pseudonym is valid.")
else:
    print("The pseudonym is invalid.")
