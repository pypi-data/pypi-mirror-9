import io
import os
import unittest

from . import tags, ids


class TestEncodeAndDecode(unittest.TestCase):
    def setUp(self):
        if 'PYNBTTESTPATH' in os.environ:
            self.output = open(os.environ['PYNBTTESTPATH'], "wb+")
        else:
            self.output = io.BytesIO()
        self.maxDiff = None

    def test_roundtrip(self):
        self.data = tags.CompoundTag({
            "byte": tags.ByteTag(4),
            "short": tags.ShortTag(0x7FFF),
            "int": tags.IntTag(12345),
            "long": tags.LongTag(1),
            # Leave out float and double to avoid floating-point errors
            "unicode": tags.StringTag("Here's an acc\u00c9nt!"),
            "list": tags.ListTag([
                tags.CompoundTag({
                    "name": tags.StringTag("foo"),
                    "value": tags.IntTag(12),
                }),
                tags.CompoundTag({
                    "name": tags.StringTag("bar"),
                    "value": tags.IntTag(21),
                }),
            ], ids.TAG_Compound),
            "bytearray": tags.ByteArrayTag(b"Hello world!"),
            "intlist": tags.IntArrayTag([1, 2, 3]),
        })
        self.do_roundtrip()
        self.assertEqual(self.lvalues, self.rvalues)

    def test_pathological(self):
        self.data = tags.CompoundTag({
            "list": tags.ListTag([tags.EndTag(), tags.EndTag(),
                                  tags.EndTag()], ids.TAG_End),
        })
        self.do_roundtrip()
        self.assertEqual(self.lvalues, self.rvalues)

    def do_roundtrip(self):
        enclen = self.data.encode_named("", self.output)
        self.output.seek(0)
        decname, decoded = tags.decode_named(self.output)
        self.lvalues = ('', self.data)
        self.rvalues = (decname, decoded)

    def tearDown(self):
        self.output.close()
