"""
Code used to classify what type of data it is, so it can be
converted to text.
"""
import array
import calendar
from collections import ChainMap, abc, deque
import enum
import numbers
from typing import Any
import datetime as dt
from zoneinfo import ZoneInfo


class DataTypeIdentification:
    """
    This class contains methods to classify/identify
    an unknown object.
    """

    def is_bytes(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `bytes`. False otherwise.
        """
        return isinstance(data, bytes)

    def is_bytearray(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `bytearray`. False otherwise.
        """
        return isinstance(data, bytearray)

    def is_binary(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `bytes` or `bytearray`. False otherwise.
        """
        return self.is_bytes(data) \
            or self.is_bytearray(data)

    def is_bool(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `bool`. False otherwise.
        """
        return isinstance(data, bool) and str(type(data)) == "<class 'bool'>"

    def is_calendar(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `calendar`. False otherwise.
        """
        return isinstance(data, calendar.Calendar)

    def is_chainmap(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `ChainMap`. False otherwise.
        """
        return isinstance(data, ChainMap)

    def is_date(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `dt.date` or `dt.datetime`. False otherwise.
        """
        return isinstance(data, dt.date) and not isinstance(data, dt.datetime)

    def is_datetime(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `dt.datetime`. False otherwise.
        """
        return isinstance(data, dt.datetime)

    def is_dict(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `dict` or `abc.Mapping`. False otherwise.
        """
        return isinstance(data, dict) or isinstance(data, abc.Mapping)

    def is_enum(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `enum`. False otherwise.
        """
        return isinstance(data, enum.Enum)

    def is_namedtuple(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of a `namedtuple`. False otherwise.
        """
        # type: ignore
        return (
            isinstance(data, tuple) and
            hasattr(data, '_asdict') and  # type: ignore
            hasattr(data, '_fields')  # type: ignore
        )

    def is_none(self, data: Any) -> bool:
        """
        Returns:
            bool: True if is None. False otherwise.
        """
        return data is None

    def is_numeric(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `numbers.Number` or `enum`.
            But excludes `bool`. False otherwise.
        """
        return (
            isinstance(data, numbers.Number)  # type: ignore
            and (not isinstance(data, enum.Enum))
            and str(type(data)) != "<class 'bool'>"  # type: ignore
        )

    def is_sequence(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data has a sequence of data, eg List, etc. False otherwise.
        """
        return isinstance(data, list | tuple | set | range | array.array | deque | abc.Iterator) \
            and not self.is_namedtuple(data) \
            and not self.is_dict(data)

    def is_str(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `str`. False otherwise.
        """
        return isinstance(data, str)

    def is_time(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `dt.time`. False otherwise.
        """
        return isinstance(data, dt.time)

    def is_timedelta(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `dt.timedelta`. False otherwise.
        """
        return isinstance(data, dt.timedelta)

    def is_timezone(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `dt.timezon`. False otherwise.
        """
        return isinstance(data, dt.timezone)

    def is_zoneinfo(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `ZoneInfo`. False otherwise.
        """
        return isinstance(data, ZoneInfo)

    def is_tzinfo(self, data: Any) -> bool:
        """
        Returns:
            bool: True if data is an instance of `dt.tzinfo`. False otherwise.
        """
        return isinstance(data, dt.tzinfo) \
            and not self.is_timezone(data) \
            and not self.is_zoneinfo(data)
