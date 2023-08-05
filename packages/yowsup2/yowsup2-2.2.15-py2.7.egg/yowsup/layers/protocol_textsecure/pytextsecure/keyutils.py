#!/usr/bin/env python3

#from nacl.public import PrivateKey, PublicKey

from random import SystemRandom

import base64

from database import TextSecureDatabase#session


from sqlalchemy import exists
from dbmodel import PreKey, PreKeyIndex, IdentityKey, RecipientPreKey, ChatSession, Recipients

from curve25519 import keys
import curve25519
import ed25519

def getSession():
    return TextSecureDatabase.get().session

def genKey():
    key = keys.Private()
    privkey = key.private
    pubkey = key.get_public().serialize()
    return privkey, pubkey


class PreKeyUtil:
    BATCH_SIZE = 199
    MAX_PRE_KEY = 0xFFFFFF

    def __init__(self):
        #self.py = shelve.open('state/prekeysdb')
        pass

    #def getPreKey(self, keyId):
    #    return session.query(PreKey).filter(PreKey.keyId==keyId).first()

    def getPreKey(self, keyId):
        return getSession().query(PreKey).filter(PreKey.keyId == keyId).first().publicKey

    def getPreKeyPrivate(self, keyId):
        return getSession().query(PreKey).filter(PreKey.keyId == keyId).first().privateKey

    def getPreKeyKeyPair(self, keyId):
        publicKey = getSession().query(PreKey).filter(PreKey.keyId == keyId).first().publicKey
        privateKey = getSession().query(PreKey).filter(PreKey.keyId == keyId).first().privateKey
        return publicKey, privateKey

    def getPreKeys(self):
        return getSession().query(PreKey).filter(PreKey.keyId != self.MAX_PRE_KEY)

    def getLastResortKey(self):
        return getSession().query(PreKey).filter(PreKey.keyId == self.MAX_PRE_KEY).first()

    def getAndRemovePreKeyPair(self, keyId):
        #return session.query(PreKey).filter(PreKey.keyId==keyId).first()
        preKeyPair = self.getPreKeyKeyPair(keyId)
        self.deletePreKey(keyId)
        return preKeyPair

    def deletePreKey(self, keyId):
        getSession().query(PreKey).filter(PreKey.keyId == keyId).delete()

    def hasRecord(self, keyId):
        return getSession().query(exists().where(PreKey.keyId == keyId)).scalar()

    def xgenerateSignedPreKey(self):
        signedPreKeyid = self.getNextPreKeyId()
        privCurv = curve25519.Private()
        pubCurv = privCurv.get_public()

        privateKey = privCurv.serialize()
        publicKey= pubCurv.serialize()

        signingKey,verifyingKey = ed25519.create_keypair()

        signedKey= signingKey.sign(publicKey)
        return (signedKey, verifyingKey.to_bytes())


        # pubCurv = privCurv.get_public()
        # privateKey = privCurv.serialize()
        # publicKey = pubCurv.serialize()
        # signingKey = ed25519.SigningKey()
        # privKey, publicKey = ed25519.create_keypair()
        # signature = privKey.sign(publicKey)
        #record = (signedPreKeyid)

    def generateSignedPreKey(self, identityKey):
        keyPair = genKey()
        signingKey = ed25519.SigningKey(identityKey)
        signature = signingKey.sign(keyPair[1])
        return(signature, keyPair)


    def generatePreKeys(self):
        keyIdOffset = self.getNextPreKeyId();

        for i in range(0, self.BATCH_SIZE):
            keyId = (keyIdOffset + i) % self.MAX_PRE_KEY;
            privkey, pubkey = genKey()
            getSession().add(PreKey(keyId=keyId,
                               publicKey=pubkey,
                               privateKey=privkey)
            )

        self.setNextPreKeyId((keyIdOffset + self.BATCH_SIZE) % self.MAX_PRE_KEY)

    def generateLastResortKey(self):
        if getSession().query(exists().where(PreKey.keyId == self.MAX_PRE_KEY)).scalar():
            return getSession().query(PreKey).filter(PreKey.keyId == self.MAX_PRE_KEY).first()

        privkey, pubkey = genKey()
        getSession().add(PreKey(keyId=self.MAX_PRE_KEY,
                           publicKey=pubkey,
                           privateKey=privkey)
        )

    def setNextPreKeyId(self, nextKeyId):
        keyIndex = getSession().query(PreKeyIndex).first()
        keyIndex.nextKeyId = nextKeyId

    def getNextPreKeyId(self):
        if not getSession().query(PreKeyIndex).count():
            getSession().add(PreKeyIndex(nextKeyId=SystemRandom().randint(0, self.MAX_PRE_KEY)))
        return getSession().query(PreKeyIndex).first().nextKeyId  #return last keyId

    def __del__(self):
        getSession().commit()


class IdentityKeyUtil:
    def __init__(self):
        #self.py = shelve.open('state/IdentityKeyId')
        pass

    def getIdentityKey(self):
        return getSession().query(IdentityKey).first().publicKey
        #rawpkey = session.query(IdentityKey).first().publicKey
        #return base64.b64encode(b'\x05' + rawpkey)

    def getIdentityPrivKey(self):
        return getSession().query(IdentityKey).first().privateKey
        #rawskey = session.query(IdentityKey).first().privateKey
        #return base64.b64encode(b'\x05' + rawskey)

    def getIdentityKeyPair(self):
        return getSession().query(IdentityKey).first()

    def generateIdentityKey(self):
        if getSession().query(IdentityKey).count():
            return

        privkey, pubkey = genKey()
        getSession().add(IdentityKey(
            publicKey=pubkey,
            privateKey=privkey)
        )

    def __del__(self):
        getSession().commit()


class RecipientPreKeyUtil:
    def __init__(self):
        #self.py = shelve.open('state/IdentityKeyId')
        pass

    def saveRecipientPreKey(self, number, response):
        for keyData in response['keys']:
            #create nacl publicKey objects
            publicKey = base64.b64decode(keyData['publicKey'])[1:]
            identityKey = base64.b64decode(keyData['identityKey'])[1:]

            getSession().add(RecipientPreKey(
                phoneNumber=number,
                deviceId=keyData['deviceId'],
                keyId=keyData['keyId'],
                publicKey=publicKey,
                identityKey=identityKey,
                registrationId=keyData['registrationId'])
            )


    def __del__(self):
        getSession().commit()


class ChatSessionUtil:
    def __init__(self):
        #self.py = shelve.open('state/IdentityKeyId')
        pass

    def getChatSession(self, number):
        if getSession().query(exists().where(ChatSession.phoneNumber == number)).scalar():
            return getSession().query(ChatSession).filter(ChatSession.phoneNumber == number).first().session
        else:
            return None

    def saveChatSession(self, number, chatsession):

        #sessionId = self.getSessionId(number)

        #if sessionId:
        #    session.query(ChatSession).filter(ChatSession.id==sessionId).delete()

        getSession().merge(ChatSession(
            phoneNumber=number,
            session=chatsession)
        )

        getSession().commit()

    def hasSession(self, number):
        return getSession().query(exists().where(ChatSession.phoneNumber == number)).scalar()

    def getSessionId(self, number):

        if self.hasSession(number):
            return getSession().query(ChatSession).filter(ChatSession.phoneNumber == number).first().id

        return None

    def deleteChatSession(self, number):
        getSession().query(ChatSession).filter(ChatSession.phoneNumber == number).delete()
        getSession().commit()


class RecipientUtil:
    def __init__(self):
        #self.py = shelve.open('state/IdentityKeyId')
        pass

    def getNumberFromAlias(self, alias):
        if getSession().query(exists().where(Recipients.alias == alias)).scalar():
            return getSession().query(Recipients).filter(Recipients.alias == alias).first().phoneNumber
        elif getSession().query(exists().where(Recipients.phoneNumber == alias)).scalar():
            return alias
        else:
            raise 'Unknown alias in getNumberFromAlias'

    def getAliasFromNumber(self, number):
        alias = getSession().query(Recipients).filter(Recipients.phoneNumber == number).first().alias
        if alias is None:
            return number
        else:
            return alias

    def getAllRecipients(self):
        return getSession().query(Recipients)

    def saveRecipient(self, number, identityKey, alias):

        getSession().add(Recipients(
            phoneNumber=number,
            identityKey=identityKey,
            alias=alias
        ))

    def __del__(self):
        getSession().commit()


if __name__ == "__main__":
    pass
#import json
#PreKeyUtil().generatePreKeys()
#records = PreKeyUtil().getPreKeys()

#preKeys = list()
# for preKey in records:
#     preKeys.append(
#         {
#             'keyId' : preKey.keyId,
#             'publicKey' : base64.b64encode(b'\x05' + preKey.publicKey).decode("utf-8"),
#             'identityKey' : IdentityKeyUtil().getIdentityKey().decode("utf-8")
#         }
#     )

#print len(records)

# lastResortKey = PreKeyUtil().getLastResortKey()
# lastResortKeyDict = {
#             'keyId' : lastResortKey.keyId,
#             'publicKey' : base64.b64encode(b'\x05' + lastResortKey.publicKey).decode("utf-8"),
#             'identityKey' : IdentityKeyUtil().getIdentityKey().decode("utf-8")
#         }
#
# data = { 'lastResortKey' : lastResortKeyDict , 'keys' : preKeys}
#
# print(json.dumps(data))


'''
PreKeyUtil().generatePreKeys()

lastResortKey = PreKeyUtil().generateLastResortKey()
print(lastResortKey.privateKey)

IdentityKeyUtil().generateIdentityKey()
print(IdentityKeyUtil().getIdentityKey())
#records = PreKeyUtil().generatePreKeys()
records = PreKeyUtil().getPreKeys()
i = 0
for preKey in records:
    print(preKey.publicKey)
    i += 1
'''