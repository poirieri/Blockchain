import rsa


def generate_keys():
    (pubKey, privKey) = rsa.newkeys(512)
    return pubKey, privKey


def import_keys(private_key_directory):
    # import from file
    # dir: name file .pem
    with open(private_key_directory, mode='rb') as privatefile:
        key_data = privatefile.read()
        private_key = rsa.PrivateKey.load_pkcs1(key_data)
        return private_key


def encrypt(data, public_key):
    msg = data.encode('utf8')
    return rsa.encrypt(msg, public_key)


def decrypt(encrypted_data, private_key):
    msg = rsa.decrypt(encrypted_data, private_key)
    return msg.decode('utf8')


def sign_message(data, private_key):
    hash_value = rsa.compute_hash(data.encode('utf8'), 'SHA-1')  # generate hash on client machine
    signed_message = rsa.sign_hash(hash_value, private_key, 'SHA-1')  # sign  # hash with a private key
    return signed_message


def verify_message(data, signature, public_key):
    try:
        rsa.verify(data, signature, public_key)
        return 1
    except rsa.pkcs1.VerificationError:
        return 0
