import rsa


def generate_keys():
    """Generate pair of keys
    :return: generated pair of keys.
    """
    (pubKey, privKey) = rsa.newkeys(512)
    return pubKey, privKey


def import_keys(private_key_directory):
    """Import set of keys from file
    :param private_key_directory
    :return private_key.
    """
    # import from file
    # dir: name file .pem
    with open(private_key_directory, mode='rb') as privatefile:
        key_data = privatefile.read()
        private_key = rsa.PrivateKey.load_pkcs1(key_data)
        return private_key


def encrypt(data, public_key):
    """Encrypt data with public key
    :param data
    :param public_key
    :return ecrypted data.
    """
    msg = data.encode('utf8')
    return rsa.encrypt(msg, public_key)


def decrypt(encrypted_data, private_key):
    """Decrypt data with private key
    :param encrypted_data:
    :param private_key:
    :return: decrypted data.
    """
    msg = rsa.decrypt(encrypted_data, private_key)
    return msg.decode('utf8')


def sign_message(data, private_key):
    """Sign data with signature.
    :param data:
    :param private_key:
    :return: signed_message with hash_value.
    """
    hash_value = rsa.compute_hash(data.encode('utf8'), 'SHA-1')  # generate hash on client machine
    signed_message = rsa.sign_hash(hash_value, private_key, 'SHA-1')  # sign  # hash with a private key
    return signed_message


def verify_message(data, signature, public_key):
    """
    :param data:
    :param signature:
    :param public_key:
    :return: True if signature is connected with data or false when not.
    """
    try:
        rsa.verify(data, signature, public_key)
        return True
    except rsa.pkcs1.VerificationError:
        return False
