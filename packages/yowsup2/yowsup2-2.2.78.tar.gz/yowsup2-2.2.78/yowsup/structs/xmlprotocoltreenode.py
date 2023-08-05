from lxml import etree

class ProtocolTreeNode(etree.ElementBase):
    parser = None

    def __init__(self, tag, attributes, children, data):
        pass

    @staticmethod
    def new(tag, attributes = None, children = None , data = None):
        ProtocolTreeNode.__ensureParser()
        attributes = attributes or {}
        children = children or []

        element = ProtocolTreeNode.parser.makeelement(tag)
        element.setData(data)
        element.addChildren(children)
        for k, v in attributes.items():
            element.setAttribute(k, v)

        return element
    def getTag(self):
        return self.tag

    @staticmethod
    def __ensureParser():
        if ProtocolTreeNode.parser is None:
            ProtocolTreeNode.parser = etree.XMLParser()
            ProtocolTreeNode.parser.set_element_class_lookup(
                 etree.ElementDefaultClassLookup(element = ProtocolTreeNode)
            )

    @staticmethod
    def fromXML(xml):
        ProtocolTreeNode.__ensureParser()
        return etree.fromstring(xml, ProtocolTreeNode.parser)

    def __eq__(self, protocolTreeNode):
        """
        :param protocolTreeNode: ProtocolTreeNode
        :return: bool
        """
        #
        if protocolTreeNode.__class__ == ProtocolTreeNode \
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
            result[k] = self.getAttributeValue(k)

        return result

    def getLocalName(self):
        tag = self.getTag()
        return tag.split(':')[1] if ':' in tag else tag

    def toPrettyXml(self):
        return etree.tostring(self, pretty_print = True)

    def __str__(self, ensureNamespace = True):
        if ensureNamespace and ":" in self.getTag():
            ns = self.getTag().split(':')[0]
            attrib = "xmlns:%s" % ns
            if not self.hasAttribute(attrib):
                self.setAttribute(attrib, ns)
                result = self.toPrettyXml()
                self.removeAttribute(attrib)
                return result

        return self.toPrettyXml()

    def getData(self):
        return self.text if self.text else None

    def setData(self, data):
        self.text = data


    @staticmethod
    def tagEquals(node,string):
        return node is not None and node.tag is not None and node.tag == string


    @staticmethod
    def require(node,string):
        if not ProtocolTreeNode.tagEquals(node,string):
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
        self.set(key ,value)

    def getAllChildren(self,tag = None):
        return self.findall(tag) if tag is not None else self[:]
