from yowsup.layers import YowProtocolLayer
from pytextsecure import keyutils, database, dbmodel
from protocolentities import SetKeysIqProtocolEntity
import os
from curve25519 import keys
from pytextsecure import ratcheting_session
import binascii
class YowTextSecureProtocolLayer(YowProtocolLayer):
    EVENT_PREKEYS_SET = "org.openwhatsapp.yowsup.events.textsecure.set"
    TYPE_DJB = 0x5
    def __init__(self):
        super(YowTextSecureProtocolLayer, self).__init__()
        #self.handleMap = {
        #    "success": (self.onSuccess, None)
        #}

    def onEvent(self, yowLayerEvent):
        if yowLayerEvent.getName() == self.__class__.EVENT_PREKEYS_SET:
            self.sendKeys()


    def _sendKeys(self):
        _privateKey = keys.Private()
        privateKey = _privateKey.serialize()
        publicKey = _privateKey.get_public().serialize()
        preKeysDict = {}
        for i in xrange(0, 200):
            prekey_id = binascii.hexlify(hex(0x100000 + i))
            preKeysDict[prekey_id] = publicKey

    def sendKeys(self):
        db_path = "/home/tarek/config.db"
        newDb = not os.path.exists(db_path)

        tsb = database.TextSecureDatabase("sqlite:///%s" % db_path)
        tsb.init_db(dbmodel.Base)
        pku = keyutils.PreKeyUtil()
        identityu = keyutils.IdentityKeyUtil()
        if True:
            pku.generatePreKeys()
            identityu.generateIdentityKey()

            preKeys = pku.getPreKeys()
            preKeysDict = {}
            for preKey in preKeys:
                strKeyId = str(preKey.keyId)
                if len(strKeyId) % 2:
                    strKeyId = "0" + strKeyId
                preKeysDict[strKeyId.decode('hex')] = preKey.publicKey

            #signedkey = ("000000".decode("hex"), preKeys[0].publicKey, "abc")
            #signedKey = pku.generateSignedPreKey(identityu.getIdentityPrivKey())
            #signedkeyTuple = ("000000".decode("hex"), signedKey[1][0], signedKey[0])
            #keyPair = keyutils.genKey()
            keyPair = ratcheting_session.Curve().generateKeyPair()
            print keyPair.publicKey.serialize()
            signature = ratcheting_session.Curve().calculateAgreement(identityu.getIdentityPrivKey(), keyPair.publicKey.serialize())
            signedkeyTuple = ("000000".decode("hex"), keyPair.privateKey.serialize(), signature)

            setKeysIq = SetKeysIqProtocolEntity(identityu.getIdentityKey(), signedkeyTuple, preKeysDict, self.__class__.TYPE_DJB)
            self.toLower(setKeysIq.toProtocolTreeNode())
            print(setKeysIq.toProtocolTreeNode())
