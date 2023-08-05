class ProtocolEntityMeta(type):
    def __new__(cls, clsname, bases, dct):
        schema = dct["schema"]

        return super(ProtocolEntityMeta, cls).__new__(cls, clsname, bases, dct)


class ProtocolEntity(object):
    __metaclass__ = ProtocolEntityMeta
    schema = None

class AckProtocolEntity(ProtocolEntity):
    schema = "a.xsd"

if __name__ == "__main__":
    a = AckProtocolEntity()