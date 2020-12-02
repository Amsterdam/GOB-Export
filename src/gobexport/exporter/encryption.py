import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from gobexport.config import get_public_key

DELIMITER = b':'


def _encrypt_symmetric_key(public_key, symmetric_key):
    """ Encrypt a symmetric key using an asymmetric public key.

    The result is a base64 encoded key, which will be embedded in the result

    :param key_name: The name of the public key to use
    """
    with open(public_key, 'rb') as key:
        public_key = serialization.load_pem_public_key(
            key.read(),
            backend=default_backend()
        )

    encrypted_key = public_key.encrypt(
        symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))

    # Base64 encrypt the key for transport
    return base64.b64encode(encrypted_key)


def encrypt_file(file_name, key_name):
    """ Encrypt a file using symmetric encryption and encrypt the symmetric key using an asymmetric public key.

    The result is a file with the key length, the encrypted symmetric key, and the encrypted data. This hybrid approach
    is chosen because asymmetrical encryption is not suited for large files.

    :param file_name: The file_name of the file to encrypt
    :param key_name: The name of the public key to use
    """
    public_key = get_public_key(key_name)

    symmetric_key = Fernet.generate_key()

    with open(file_name, "rb") as file:
        unencrypted_data = file.read()

    # Encrypt the data in the file using Fernet
    f = Fernet(symmetric_key)
    encrypted_data = f.encrypt(unencrypted_data)

    # Encrypt the symmetric key using the public key
    encrypted_symmetric_key = _encrypt_symmetric_key(public_key, symmetric_key)

    # The first 4 bytes of the file will be the length of the encrypted_symmetric_key
    key_length = f'{len(encrypted_symmetric_key):04}'.encode()

    # Save the key length, encrypted key and data separated by dots to the file
    with open(file_name, 'wb') as file:
        file.write(DELIMITER.join([key_length, encrypted_symmetric_key, encrypted_data]))
