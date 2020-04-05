### Generating keys
import rsa


def generate_keys():
    (pubKey, privKey) = rsa.newkeys(512)
    return pubKey, privKey


def import_keys(privkeydir):

# import from file
# dir: name file .pem
    with open(privkeydir, mode='rb') as privatefile:
         keydata = privatefile.read()
         privkey = rsa.PrivateKey.load_pkcs1((keydata))


def encrypt(data, pubKey):
    # return rsa.encrypt(data.encode('utf8'), pub_key)
    msg = data.encode('utf8')
    return rsa.encrypt(msg, pubKey)


def decrypt(encryptedData, privKey):
    # return (rsa.decrypt(encryptedData, privKey)).decode('utf8')
    msg = rsa.decrypt(encryptedData, privKey)
    return msg.decode('utf8')


def signMessage(data, privKey):
    hash = rsa.compute_hash(data, 'SHA-1') # generate hash on client machine
    return rsa.sign(hash, privKey, 'SHA-1') # sign hash with a private key


def verifyMessage(data, signature, pubKey):
    try:
        rsa.verify(data, signature, pubKey)
        return 1
    except rsa.pkcs1.VerificationError:
        return 0


# if __name__ == '__main__':
#     pub, priv = generate_keys()
#     msg = encrypt("test", pub)
#     print(msg)
#     msg = decrypt(msg, priv)
#     print(msg)