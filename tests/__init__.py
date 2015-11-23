import unittest2
import twelve
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
            twelve.utcnow(),
            datetime.timedelta(days=5, hours=4, minutes=3, seconds=2),
        ]
        for c in cases:
            self.assertEqual(c, twelve.parse(twelve.dump(c)))

class BlobEncodingTest(unittest2.TestCase):
    def testCase(self):
        s = "Hello, World"
        a = twelve.blob(s)
        b = twelve.parse(twelve.dump(a))

        self.assertEqual(s, b.fh.read())

        s = "Hello, World"
        a = twelve.blob(BytesIO(s))
        b = twelve.parse(twelve.dump(a))

        self.assertEqual(s, b.fh.read())



if __name__ == '__main__':
    unittest2.main()
