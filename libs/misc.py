"""
Miscellaneous helper functions.
"""
import platform
from typing import Any, Dict, Optional, cast
import tzlocal


def coalesce(*values: Any) -> Optional[Any]:
    """Return the first non-None value or None if all values are None"""
    return next((v for v in values if v is not None), None)


def iswindows() -> bool:
    """
    Test whether we are running on Windows.

    Returns:
        bool: True if running on Windows, otherwise False.
    """
    return platform.system() == 'Windows'


def ismac() -> bool:
    """
    Test whether we are running on Mac.

    Returns:
        bool: True if running on Mac, otherwise False.
    """
    return platform.system() == 'Darwin'


def islinux() -> bool:
    """
    Test whether we are running on Linux.

    Returns:
        bool: True if running on Linux, otherwise False.
    """
    return platform.system() == 'Linux'


def convert_windows_tz_name_to_iani_name(tzname: str) -> str:
    """
    Convert a timezone name from windows format 'AUS Eastern Standard Time'
    to IANA 'Australia/Sydney'.

    Args:
        tzname (str): Name of a timezone. If IANA 'Australia/Sydney' is
        already in the format, then it is returned unchanged. If the tzname
        cannot be matched, then tzname is returned.

    Returns:
        str: Returns the IANA timezone name.
    """
    wintz: Dict[str, str] = cast(Dict[str, str], tzlocal.win32.win_tz)  # type: ignore
    if tzname in wintz.values():
        # Nothing to do, the name is in the correct format
        return tzname
    elif tzname in wintz.keys():  # pylint: disable=C0201; consider-iterating-dictionary
        # Convert it to the standar IANA name
        return wintz[tzname]
    else:
        # assume the name is in IANA format
        return tzname
