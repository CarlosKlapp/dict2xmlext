from typing import Optional
import codecs


class CodecWrapper:
    _codecinfo: Optional[codecs.CodecInfo] = None
    codec_error_handler: str = 'surrogatepass'
    ''' see https://docs.python.org/3/library/codecs.html#codec-base-classes for valid values'''
    _codec_name: str = 'utf_8'

    @ property
    def codec_name(self) -> str:
        return self._codec_name

    @ codec_name.setter
    def codec_name(self, codec_name: str) -> None:
        self._codec_name = codec_name

    @ property
    def codec(self) -> codecs.CodecInfo:
        if (self._codecinfo is None):
            self._codecinfo = codecs.lookup(self._codec_name)
        else:
            assert self._codecinfo.name is not None
            if (self._codecinfo.name.lower() != self._codec_name.lower()):
                self._codecinfo = codecs.lookup(self._codec_name)

        self._codec_name = self._codecinfo.name
        return self._codecinfo

    @ codec.setter
    def codec(self, codecinfo: codecs.CodecInfo) -> None:
        self._codec_name = codecinfo.name
        self._codecinfo = codecinfo
