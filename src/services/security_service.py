import base64

from ast import literal_eval as tuple_from_str

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sympy.crypto import crypto


class SecurityService:

    def __init__(self):
        self.pri_key = None
        self.pub_key = None
        self.cipher = None
        self.generate_keys()

    def generate_keys(self):
        pri_key = crypto.dh_private_key(25)
        pub_key = crypto.dh_public_key(pri_key)

        self.pri_key = pri_key
        self.pub_key = pub_key

        print('my private key: {}'.format(pri_key))
        print('my public key: {}'.format(pub_key))

    def set_friend_pub_key(self, pub_key_received_str):
        print("Receiving pub_key {}".format(pub_key_received_str))
        pub_key_received = tuple_from_str(pub_key_received_str)
        shared_key = crypto.dh_shared_key(pub_key_received, self.pri_key[2])
        print('"Shared" key: {}'.format(shared_key))

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'',
            iterations=100000,
            backend=default_backend()
        )

        b_shared_key = str(shared_key).encode()
        key = base64.urlsafe_b64encode(kdf.derive(b_shared_key))
        print("Key used to encrypt/decrypt data: {}".format(key))
        self.cipher = Fernet(key)

    def encrypt(self, msg_bytes):
        return self.cipher.encrypt(msg_bytes)

    def decrypt(self, msg_bytes):
        return self.cipher.decrypt(msg_bytes)
