import unittest
import binascii
from axolotl.protocol.whispermessage import WhisperMessage
from axolotl.protocol.prekeywhispermessage import PreKeyWhisperMessage
class TestCoderus(unittest.TestCase):
    def test_whisper(self):
        serialized = "230a21056013e4e2a2f72d131b5b10f760b46f9c087fbb33ef67baa26ed9b17e68a8963a10"
        serialized = "330a21053ac1b1b52beb88f4cffcbc92c39760b593da0c691d82133a0d881e9ee9a2bb621031180022301d9b8af1626a2e379baabb0ec1b299c2965aa40d4c0408b6c2001d60ac317dd880bedc185b51753cc5f5bfdd9c2336c055afcaadaa673f2a"
        serialized = binascii.unhexlify(serialized)
        # whisper = WhisperMessage(serialized = serialized)
        # prewhisperSerialized = "2308e9f401122105f36285d7e388e014b15dbc035202c0d6dcd7ece4e811d374cc5c91462c4889341a2105ce34be348f012e18d25914131713588f15f3f0c3ad56e72a7c1d4910d542a9292225230a21059d5ee0bb2ba7843e06c08dcb2f611ab7112ae516c8ae2a31625e0d9ed4baf10e10289192d3b20f3000"
        prewhisperSerialized = "2308e9f401122105db5e6eb1a65595ae56482995a94fb9400af928d4d73bb548ed493c13a305bb3d1a2105f08eef48c14f94c7c5ebc9fb5c7dc6fe867567920c285aa90983220d2509b94c2256230a2105767fc2f37de0b8130e1808cf6b505c636d118adcb99f793d14f5bc263a6ae44610001800222466b9df118ebd28c7064ef7f6c0366205bf56160e6592c6358311944402e3167382f8670298653b59b1cbf76d28fbb4d8fb093000"
        prewhisperSerialized = binascii.unhexlify(prewhisperSerialized)
        p = PreKeyWhisperMessage(serialized=prewhisperSerialized)