from yowsup.layers.stanzaregulator import YowStanzaRegulator
import unittest
class YowStanzaRegulatorTest(unittest.TestCase):
    def test_x(self):
        layer = YowStanzaRegulator()
        layer.buf = [128, 0, 9, 49, 198, 4, 155, 200, 234, 97, 136, 25]
        layer.processReceived()