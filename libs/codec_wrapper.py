"""
Wrapper to handle codec encoders.
"""
from typing import Optional
import codecs


class CodecWrapper:
    """
    Wrapper to handle the instantion of a codec.
    """

    _codecinfo: Optional[codecs.CodecInfo] = None
    """
    Store the codec information loaded from the codec registry.
    """

    codec_error_handler: str = 'surrogatepass'
    """
    Flag indicating how we are going to handle errors. By default the flag is set
    to `surrogatepass`.

    see https://docs.python.org/3/library/codecs.html#codec-base-classes for valid values
    https://docs.python.org/3/library/codecs.html#binary-transforms
    """

    _codec_name: str = 'utf_8'
    """
    Name of the default codec we will be using. By default it is `UTF-8`.
    """

    @ property
    def codec_name(self) -> str:
        """
        Getter for the codec name.

        Returns:
            str: Current codec name.
        """
        return self._codec_name

    @ codec_name.setter
    def codec_name(self, codec_name: str) -> None:
        """
        Setter for the codec name.

        Args:
            codec_name (str): Name of a valid codec.
        """
        self._codec_name = codec_name

    @ property
    def codec(self) -> codecs.CodecInfo:
        """
        Getter for the codec. If the codec has not been loaded,
        load it now.

        Returns:
            codecs.CodecInfo: Return the loaded CodecInfo class.
        """

        if self._codecinfo is None:
            self._codecinfo = codecs.lookup(self._codec_name)
        else:
            assert self._codecinfo.name is not None
            # A codec is already loaded, but is it the one we want?
            if self._codecinfo.name.lower() != self._codec_name.lower():
                self._codecinfo = codecs.lookup(self._codec_name)

        # Get the official codec name.
        self._codec_name = self._codecinfo.name
        return self._codecinfo

    @ codec.setter
    def codec(self, codecinfo: codecs.CodecInfo) -> None:
        """
        Setter for the codecinfo.

        Args:
            codecinfo (codecs.CodecInfo): A codec that has been previously loaded.
        """
        self._codec_name = codecinfo.name
        self._codecinfo = codecinfo
