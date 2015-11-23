import unittest2
import twelve as glyph
import datetime
import collections

from cStringIO import StringIO
from io import BytesIO

class EncodingTest(unittest2.TestCase):
    def testCase(self):
        cases = [
            1,
            1.0,
            "foo",
            u"bar",
            [],
            ['a',1,[2]],
            collections.OrderedDict([('a', 1), ('b',2)]),
            None,
            True,
            False,
            {'a':1},
            set([1,2,3]),
            glyph.utcnow(),
            datetime.timedelta(days=5, hours=4, minutes=3, seconds=2),
        ]
        for c in cases:
            self.assertEqual(c, glyph.parse(glyph.dump(c)))

class BlobEncodingTest(unittest2.TestCase):
    def testCase(self):
        s = "Hello, World"
        a = glyph.blob(s)
        b = glyph.parse(glyph.dump(a))

        self.assertEqual(s, b.fh.read())

        s = "Hello, World"
        a = glyph.blob(BytesIO(s))
        b = glyph.parse(glyph.dump(a))

        self.assertEqual(s, b.fh.read())



if __name__ == '__main__':
    unittest2.main()
