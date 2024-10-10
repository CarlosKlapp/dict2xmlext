"""
Concrete class for configuration. This class
can be used for production.
"""

from typing import override
from libs.abstract_baseclasses import ConfigBaseClass
from libs.data_processor import (
    DataProcessor_binary,
    DataProcessor_bool,
    DataProcessor_calendar,
    DataProcessor_ChainMap,
    DataProcessor_date,
    DataProcessor_datetime,
    DataProcessor_dict,
    DataProcessor_enum,
    DataProcessor_last_chance,
    DataProcessor_none,
    DataProcessor_numeric,
    DataProcessor_namedtuple,
    DataProcessor_post_processor_for_classes,
    DataProcessor_sequence,
    DataProcessor_str,
    DataProcessor_time,
    DataProcessor_timedelta,
    DataProcessor_timezone,
    DataProcessor_tzinfo,
    DataProcessor_zoneinfo,
)
from libs.data_type_identification import DataTypeIdentification


class Config(ConfigBaseClass):
    """
    Concrete base class for holding configuration information.
    Can be used for production.
    """

    @override
    def __init__(self):
        super().__init__()

        self.default_processors.extend([
            DataProcessor_binary(self),
            DataProcessor_bool(self),
            DataProcessor_calendar(self),
            DataProcessor_ChainMap(self),
            DataProcessor_date(self),
            DataProcessor_datetime(self),
            DataProcessor_dict(self),
            DataProcessor_enum(self),
            DataProcessor_none(self),
            DataProcessor_numeric(self),
            DataProcessor_namedtuple(self),
            DataProcessor_sequence(self),
            DataProcessor_str(self),
            DataProcessor_time(self),
            DataProcessor_timedelta(self),
            DataProcessor_timezone(self),
            DataProcessor_tzinfo(self),
            DataProcessor_zoneinfo(self),
        ])
        self.custom_post_processors.append(DataProcessor_post_processor_for_classes(self))
        self.last_chance_processor = DataProcessor_last_chance(self)
        self.data_type_identification = DataTypeIdentification()
