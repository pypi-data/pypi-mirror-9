from lxml import etree
import binascii
import sys

def ProtocolTreeNode(tag = None, attributes = None, children = None , data = None, ns = None, xmlString = None, dataEncoding = None):
    assert bool(tag) ^ bool(xmlString), "Must provide either tag or xmlString"

    if tag and ":" in tag:
        tagNS, tagName = tag.split(':')
        tag = "{%s}%s" % (tagNS, tagName)
        if not ns:
            ns = (tagNS, tagNS)

    return _ProtocolTreeNode.new(tag, attributes, children, data, ns, dataEncoding) if tag else _ProtocolTreeNode.fromXML(xmlString)

class _ProtocolTreeNode(etree.ElementBase):
    parser = None

    hexlify = ("response", "success", "challenge", "registration", "identity", "value", "id", "signature", "enc", "type")

    @staticmethod
    def new(tag, attributes = None, children = None , data = None, ns = None, dataEncoding = None):
        _ProtocolTreeNode.__ensureParser()
        attributes = attributes or {}
        children = children or []
        if dataEncoding is None and tag in _ProtocolTreeNode.hexlify:
            dataEncoding = "hex"
        nsmap = {}

        if ns is not None:
            nsmap[ns[0]] = ns[1]

        element = _ProtocolTreeNode.parser.makeelement(tag, nsmap = nsmap)
        element.setData(data, dataEncoding)
        element.addChildren(children)
        for k, v in attributes.items():
            element.setAttribute(k, v)

        return element

    def getTag(self):
        return self.tag

    @staticmethod
    def __ensureParser():
        if _ProtocolTreeNode.parser is None:
            _ProtocolTreeNode.parser = etree.XMLParser()
            _ProtocolTreeNode.parser.set_element_class_lookup(
                 etree.ElementDefaultClassLookup(element = _ProtocolTreeNode)
            )

    @staticmethod
    def fromXML(xml):
        _ProtocolTreeNode.__ensureParser()
        return etree.fromstring(xml, _ProtocolTreeNode.parser)


    def __getitem__(self, key):
        if type(key) is str:
            return self.getAttributeValue(key)
        return super(_ProtocolTreeNode, self).__getitem__(key)

    def __setitem__(self, key, val):
        if type(key) is str:
            return self.setAttribute(key, val)
        return super(_ProtocolTreeNode, self).__setitem__(key, val)


    def __delitem__(self, key):
        if type(key) is str:
            return self.removeAttribute(key)
        return super(_ProtocolTreeNode, self).__delitem__(key)


    def __eq__(self, protocolTreeNode):
        """
        :param protocolTreeNode: ProtocolTreeNode
        :return: bool
        """
        #

        if protocolTreeNode.__class__ == _ProtocolTreeNode \
                and self.getTag() == protocolTreeNode.getTag() \
                and self.getData()  == protocolTreeNode.getData() \
                and self.getAttributes() == protocolTreeNode.getAttributes() \
                and len(self.getAllChildren()) == len(protocolTreeNode.getAllChildren()):
            found = False
            for c in self.getAllChildren():
                for c2 in protocolTreeNode.getAllChildren():
                    if c == c2:
                        found = True
                        break
                if not found:
                    return False

            found = False
            for c in protocolTreeNode.getAllChildren():
                for c2 in self.getAllChildren():
                    if c == c2:
                        found = True
                        break
                if not found:
                    return False

            return True

        return False

    def __hash__(self):
        return hash(self.tag) ^ hash(tuple(self.getAttributes().items())) ^ hash(self.getData())

    def getAttributes(self):
        result = {}
        for k in self.attrib:
            if k.startswith("meta-yowsup"):
                continue
            result[k] = self.getAttributeValue(k)

        return result

    def getLocalName(self):
        tag = self.getTag()
        return tag.split(':')[1] if ':' in tag else tag

    def toPrettyXml(self):
        return etree.tostring(self, pretty_print = True)

    def __str__(self, ensureNamespace = True):
        # if ensureNamespace and ":" in self.getTag():
        #     ns = self.getTag().split(':')[0]
        #     attrib = "xmlns:%s" % ns
        #     if not self.hasAttribute(attrib):
        #         self.setAttribute(attrib, ns)
        #         result = self.toPrettyXml()
        #         self.removeAttribute(attrib)
        #         return result

        result = self.toPrettyXml()
        if type(result == bytes):
            result = result.decode('utf-8')

        return result


    def getData(self):
        if self.text:
            encoding = self.getMetaAttribute("encoding", "unicode_escape")
            if encoding == "hex":
                data = binascii.unhexlify(self.text.encode()).decode("latin-1")
            else:
                data = self.text.encode().decode(encoding)
            if sys.version_info < (3,0) and type(data) is unicode:
                data = data.encode("latin-1")
            return data

    def setData(self, data, dataEncoding = None):
        if data is not None:
            if type(data) is bytes:
                data = data.decode('latin-1')

            if dataEncoding:
                self.setMetaAttribute("encoding", dataEncoding)
            else:
                dataEncoding = "unicode_escape"

            if dataEncoding == "hex":
                self.text = binascii.hexlify(data.encode("latin-1"))
            else:
                self.text = data.encode(dataEncoding)

    def setMetaAttribute(self, key, val):
        self.setAttribute("meta-yowsup-" + key, val)

    def getMetaAttribute(self, key, default = None):
        return self.getAttributeValue("meta-yowsup-" + key) or default

    def _getData(self):
        if self.text:
            hexEncoded = self.text.startswith("0x")
            if not hexEncoded:
                return self.text

            data = binascii.unhexlify(self.text[2:])
            return data #if sys.version_info < (3, 0) else data.decode()

    def _setData(self, data):
        if data:
            try:
                self.text = data
            except ValueError:
                if type(data) is not bytes:
                    data = data.encode()

                self.text = binascii.hexlify(data)
                self.text = "0x" + self.text

                # if sys.version_info < (3,0):
                #     self.text =  "0x" + binascii.hexlify(data)
                # else:
                #     self.text =  binascii.hexlify(data)


    @staticmethod
    def tagEquals(node,string):
        return node is not None and node.tag is not None and node.tag == string


    @staticmethod
    def require(node,string):
        if not _ProtocolTreeNode.tagEquals(node,string):
            raise Exception("failed require. string: "+string)

    def hasAttribute(self, attr):
        return attr in self.attrib

    def getChild(self,identifier):

        if type(identifier) == int:
            if len(self.getAllChildren()) > identifier:
                return self.getAllChildren()[identifier]
            else:
                return None
        for c in self.getAllChildren():
            if c.getTag(

            ) == identifier:
                return c


    def hasChildren(self):
        return len(self.getAllChildren()) > 0

    def addChild(self, childNode):
        self.append(childNode)

    def addChildren(self, children):
        for c in children:
            self.addChild(c)

    def getAttributeValue(self,string):
        val = self.get(string)
        return val if val != '' else None

    def removeAttribute(self, key):
        if key in self.attrib:
            del self.attrib[key]

    def setAttribute(self, key, value):
        if type(value) is int:
            value = str(value)
        self.set(key ,value)

    def getAllChildren(self,tag = None):
        return self.findall(tag) if tag is not None else self[:]

import os

class ProtocolEntityMeta(type):
    __BASE_SCHEMA = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:complexType name="yowsup_encodable" xml:base="xs:string" mixed="true">
            <xs:attribute name="meta-yowsup-encoding" use="optional" type="xs:string" />
        </xs:complexType>
        </xs:schema>
"""
    def __new__(cls, clsname, bases, dct):

        if "schema" not in dct:
            dct["schema"] = bases[0].schema
        elif dct["schema"] is not None:
            schemaXML = cls.getSchemaXML(dct["schema"])
            baseSCHEMA = etree.XML(ProtocolEntityMeta.__BASE_SCHEMA)
            for i in range(len(baseSCHEMA) -1, -1, -1):
                schemaXML.append(baseSCHEMA[i])

            parentSchemaNode = schemaXML.find("xs:redefine", namespaces={"xs": "http://www.w3.org/2001/XMLSchema"})
            if parentSchemaNode is not None:
                parentSchemaPath = parentSchemaNode.get("schemaLocation")
                originalSchemaPathDir = os.path.dirname(dct["schema"])
                targetPath = os.path.join(originalSchemaPathDir, parentSchemaPath)
                parentSchemaNode.set("schemaLocation", targetPath)

            dct["schema"] = etree.XMLSchema(schemaXML)

        originalToProtocolTreeNode = dct["toProtocolTreeNode"] if "toProtocolTreeNode" in dct else None
        def toProtocolTreeNodeWrapper(instance):
            result = originalToProtocolTreeNode(instance)

            if dct["schema"] and not cls.isValid(result.__str__(True), dct["schema"]):
                raise ValueError("Schema and XML don't match")

            return result
        if originalToProtocolTreeNode:
            dct["toProtocolTreeNode"] = toProtocolTreeNodeWrapper

        return super(ProtocolEntityMeta, cls).__new__(cls, clsname, bases, dct)

    @classmethod
    def isValid(cls, xml, schema):
        parsedXML = etree.fromstring(xml)
        return schema.validate(parsedXML)

    @classmethod
    def getSchemaXML(cls, stringOrPath):
        schemaData = stringOrPath
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), stringOrPath)
        if os.path.exists(path):
            with open(path) as schemaFile:
                schemaData = schemaFile.read()

        return etree.XML(schemaData)

class ProtocolEntity(object):
    __metaclass__ = ProtocolEntityMeta

    schema = None
    def toProtocolTreeNode(self):
        print("Base toProtocolTreeNode")

    @staticmethod
    def fromProtocolTreeNode(protocolTreeNode):
        print("Base from protocoltreenode")

    @classmethod
    def fromXML(cls, xml):
        if cls.isValid(xml):
            return cls.fromProtocolTreeNode(ProtocolTreeNode(xmlString = xml))
        else:
            raise ValueError("Invalid XML for this schema")

    @classmethod
    def isValid(cls, xml):
        parser = etree.XMLParser(schema = cls.schema)
        etree.fromstring(xml, parser)
        parsedXML = etree.XML(xml) if type(xml) is str else xml
        return cls.schema.validate(parsedXML)


class StreamFeaturesProtocolEntity(ProtocolEntity):
    schema = """<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="stream" elementFormDefault="qualified">
    <xs:element name="features" />
</xs:schema>
    """

    @staticmethod
    def fromProtocolTreeNode(protocolTreeNode):
        return StreamFeaturesProtocolEntity()

    def toProtocolTreeNode(self):
        return ProtocolTreeNode("stream:features")


class SuccessProtocolEntity(ProtocolEntity):
    schema = """
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:simpleType name="account_type">
        <xs:restriction base="xs:string">
            <xs:enumeration value="free"></xs:enumeration>
            <xs:enumeration value="paid"></xs:enumeration>
        </xs:restriction>
    </xs:simpleType>

    <xs:simpleType name="challenge">
        <xs:restriction base="xs:string">
            <xs:pattern value=".+" />
        </xs:restriction>
    </xs:simpleType>

    <xs:element name="success">
        <xs:complexType>
            <xs:simpleContent>
                <xs:extension base="challenge">
                    <xs:attribute name="creation" type="xs:long"/>
                    <xs:attribute name="expiration" type="xs:long" />
                    <xs:attribute name="kind" type="account_type" />
                    <xs:attribute name="props" type="xs:int" />
                    <xs:attribute name="status" type="xs:string" />
                    <xs:attribute name="t" type="xs:long" />
                </xs:extension>
            </xs:simpleContent>

        </xs:complexType>
    </xs:element>
 </xs:schema>
"""
    def __init__(self, challenge):
        self.challenge = challenge

    @staticmethod
    def fromProtocolTreeNode(protocolTreeNode):
        return SuccessProtocolEntity(protocolTreeNode.getData())

    def toProtocolTreeNode(self):
        return ProtocolTreeNode("success", data = self.challenge)



class MessageProtocolEntity(ProtocolEntity):
    schema = "../protocolgen/message.xsd"

    def __init__(self, _from, _type, timestamp, notify, offline):
        self._from = _from
        self._type = _type
        self.timestamp = timestamp
        self.notify = notify
        self.offline = offline

    @staticmethod
    def fromProtocolTreeNode(protocolTreeNode):
        return MessageProtocolEntity(
            protocolTreeNode.getAttributeValue("from"),
            protocolTreeNode.getAttributeValue("type"),
            protocolTreeNode.getAttributeValue("t"),
            protocolTreeNode.getAttributeValue("notify"),
            protocolTreeNode.getAttributeValue("offline")
        )

    def toProtocolTreeNode(self):
        return ProtocolTreeNode("message", {
            "from": self._from,
            "type": self._type,
            "t": self.timestamp,
            "notify": self.notify,
            "offline": self.offline,
            "id": "123"
        })

class TextMessageProtocolEntity(MessageProtocolEntity):
    schema = "../protocolgen/message_text.xsd"
    def __init__(self,body,  _from, _type, timestamp, notify, offline):
        super(TextMessageProtocolEntity, self).__init__(_from, _type, timestamp, notify, offline)
        self.body = body
    def toProtocolTreeNode(self):
        node = super(TextMessageProtocolEntity, self).toProtocolTreeNode()
        bodyNode = ProtocolTreeNode("body")
        bodyNode.setData(self.body)
        node.setData(self.body)
        return node

    @staticmethod
    def fromProtocolTreeNode(protocolTreeNode):
        entity = MessageProtocolEntity.fromProtocolTreeNode(protocolTreeNode)
        entity.__class__ = TextMessageProtocolEntity
        entity.body = protocolTreeNode.getChild("body").getData()
        return entity


class QwertyTextMessageProtocolEntity(TextMessageProtocolEntity):
    schema = "../protocolgen/message_text_abc.xsd"

#class TextMessageProtocolEntity(ProtocolEntity):


if __name__ == "__main__":

    msgXML = """<message t="1234567" from="contact_jid" offline="true" type="text" id="123456" notify="notifyJID"><body meta-yowsup-encoding="hex">7327c9da0de460dfa220619190000e2c736ad9d60b4e9f5332f010262aa70cc408044d76d6329c940996b03edbdf</body></message>
    """

    #entity = TextMessageProtocolEntity.fromXML(msgXML)
    #print(entity.body)
    #entity = QwertyTextMessageProtocolEntity.fromXML(msgXML)
    #print(entity.toProtocolTreeNode())

    #xml = "<success>abc</success>"
    #s = SuccessProtocolEntity()
    #s.toProtocolTreeNode()
    #s.fromXML("<success>abc</success>")
    # p = ProtocolTreeNode("media", {"type": "image"}, [
    #     ProtocolTreeNode("img", {"src": "abc"}, data="qwerty")
    # ])


    # entity = SuccessProtocolEntity.fromXML(xml)
    # print(entity.toProtocolTreeNode())
    #
    # entity = StreamFeaturesProtocolEntity.fromXML("<stream:features xmlns:stream=\"stream\"/>")
    # print(entity.toProtocolTreeNode())

    #print(len(p.getAllChildren()))
    #for e in p:
    #    print(e)
    #result = ElementTree.tostring(p)
    #print(etree.tostring(etree.XML(result), pretty_print = True))
    xml = '<iq type="get" id="1234" to="abc"><set></set></iq>'
    schema = """
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:ietf:params:xml:ns:xmpp-sasl">
     <xs:complexType name="yowsup_encodable" xml:base="xs:string" mixed="true">
            <xs:attribute name="meta-yowsup-encoding" use="optional" type="xs:string" />
    </xs:complexType>
    <xs:element name="response">
        <xs:complexType>
            <xs:simpleContent>
                <xs:restriction base="yowsup_encodable">
                    <xs:simpleType>
                        <xs:restriction base="xs:string">
                            <xs:pattern value=".+" />
                        </xs:restriction>
                    </xs:simpleType>
                </xs:restriction>
            </xs:simpleContent>
        </xs:complexType>
    </xs:element>
 </xs:schema>"""
    schema3 = """
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" targetNamespace="urn:ietf:params:xml:ns:xmpp-sasl">
    <xs:element name="response">
    </xs:element>
 </xs:schema>
    """
    schema4 = """
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:simpleType name="iq_type">
        <xs:restriction base="xs:string">
            <xs:enumeration value="set" />
            <xs:enumeration value="get" />
            <xs:enumeration value="result" />
        </xs:restriction>
    </xs:simpleType>

    <xs:element name="iq">
        <xs:complexType>
            <xs:attribute name="id" type="xs:string" use="required" />
            <xs:attribute name="type" type="iq_type" use="required" />
            <xs:attribute name="from" type="xs:string" use="optional" />
            <xs:attribute name="to" type="xs:string" use="optional" />
        </xs:complexType>
    </xs:element>
</xs:schema>
    """
    parsedSchemaXML = etree.XML(schema4)
    parsedSchema = etree.XMLSchema(parsedSchemaXML)
    parser = etree.XMLParser(schema = parsedSchema)
    res = etree.fromstring(xml, parser)
    print(etree.tostring(res))