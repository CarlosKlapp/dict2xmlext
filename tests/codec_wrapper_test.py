# pylint: disable=C0103,C0114,C0115,C0116,C0301
#   C0103 invalid-name
#   C0114 missing-module-docstring
#   C0115 missing-class-docstring
#   C0116 missing-function-docstring
#   C0301 line-too-long
import unittest
import codecs

from libs.codec_wrapper import CodecWrapper


class TestCodecWrapper(unittest.TestCase):

    def test_name_setter(self):
        cw = CodecWrapper()
        self.assertEqual(cw.codec_name, 'utf_8')

        cw.codec_name = 'test'
        self.assertEqual(cw.codec_name, 'test')

    def test_unknown_codec_name(self):
        cw = CodecWrapper()
        cw.codec_name = 'unknown_codec'
        self.assertEqual(cw.codec_name, 'unknown_codec')
        with self.assertRaises(LookupError) as context:
            print(cw.codec)  # try to retrieve the codec and generate an exception
        self.assertEqual('unknown encoding: unknown_codec', str(context.exception))

    def test_known_codec_name(self):
        cw = CodecWrapper()
        cw.codec_name = 'base64'
        self.assertEqual(cw.codec_name, 'base64')
        # test when coded has *not* been loaded
        codec_tmp = cw.codec
        self.assertEqual(codec_tmp, codecs.lookup('base64'))
        # test when coded has been loaded
        codec_tmp = cw.codec
        self.assertEqual(codec_tmp, codecs.lookup('base64'))
        # test when we have a codec loaded but change the name then ask for a new codec
        cw.codec_name = 'hex'
        self.assertEqual(cw.codec_name, 'hex')
        codec_tmp = cw.codec
        self.assertEqual(codec_tmp, codecs.lookup('hex'))

    def test_set_codec(self):
        cw = CodecWrapper()
        c = codecs.lookup('base64')
        cw.codec = c
        self.assertEqual(cw.codec, c)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
