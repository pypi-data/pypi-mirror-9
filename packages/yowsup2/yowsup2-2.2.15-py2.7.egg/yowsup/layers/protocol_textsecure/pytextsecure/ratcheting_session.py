from curve25519 import keys
class _DjbECPublicKey:

    DJB_TYPE = b'\x05'

    def __init__(self, publicKey):
        self.publicKey = publicKey

    def serialize(self):
        return self.DJB_TYPE + self.publicKey

class _IdentityKey:

    DJB_TYPE = b'\x05'

    def __init__(self, publicKey):
        self.publicKey = publicKey

    def serialize(self):
        return self.DJB_TYPE + self.publicKey

class _ECKeyPair():

    def __init__(self, publicKey, privateKey):
        self.publicKey = publicKey
        self.privateKey = privateKey

class _Curve:

    DJB_TYPE = 5

    # always DJB curve25519 keys
    def generateKeyPair(self, ephemeral = None):
        privateKey = keys.Private(secret=ephemeral)
        publicKey = privateKey.get_public()
        return ECKeyPair(DjbECPublicKey(publicKey.public), DjbECPublicKey(privateKey.private))

    def calculateAgreement(self, publicKey, privateKey, ephemeral=0):
        key = keys.Private(secret=privateKey)
        return key.get_shared_key(keys.Public(publicKey), lambda x: x)

    def decodePoint(self, bytes, offset=0):
        type = bytes[0] # byte appears to be automatically converted to an integer??

        if type == self.DJB_TYPE:
            type = bytes[offset] & 0xFF
            if type != self.DJB_TYPE:
                print("InvalidKeyException Unknown key type: " + str(type) )
            keyBytes = bytes[offset+1:][:32]
            return DjbECPublicKey(keyBytes)
        else:
            print("InvalidKeyException Unknown key type: " + str(type) )

    def decodePrivatePoint(self, bytes):
        return DjbECPublicKey(bytes)