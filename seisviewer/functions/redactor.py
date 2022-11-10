from datetime import datetime
from dataclasses import dataclass
import struct

import numpy as np

from seiscore import BinaryFile
from seiscore.binaryfile.binaryfile import FileInfo


def create_latitude_str(val: float) -> str:
    degrees = int(val)
    degrees_str = str(degrees).zfill(2)

    minutes = abs(val - degrees) * 60
    minutes_str = str(minutes)

    numerical_part = f'{degrees_str}{minutes_str}'[:7]
    return numerical_part.ljust(7, '0') + 'N'


def create_longitude_str(val: float) -> str:
    degrees = int(val)
    degrees_str = str(degrees).zfill(3)
    minutes = abs(val - degrees) * 60
    minutes_str = str(minutes)
    numerical_part = f'{degrees_str}{minutes_str}'[:8]
    return numerical_part.ljust(8, '0') + 'E'


def create_pseudo_sigma_header(channel_count: int,
                               datetime_start: datetime, frequency: int,
                               longitude: float, latitude: float):
    latitude_str = create_latitude_str(val=latitude)
    longitude_str = create_longitude_str(val=longitude)

    date_as_int = int(
        str(datetime_start.year)[2:] + str(datetime_start.month).zfill(2) +
        str(datetime_start.day).zfill(2)
    )

    hour_str = str(datetime_start.hour).zfill(2)
    minute_str = str(datetime_start.minute).zfill(2)
    seconds = str(datetime_start.second).zfill(2)
    time_as_int = int(hour_str + minute_str + seconds)

    header_binary = struct.pack('6H', *[0] * 6)
    header_binary += struct.pack('I', channel_count)
    header_binary += struct.pack('4H', *[0] * 4)
    header_binary += struct.pack('I', frequency)
    header_binary += struct.pack('6H', *[0] * 6)
    header_binary += struct.pack(
        '8s9s', latitude_str.encode(), longitude_str.encode()
    )
    header_binary += struct.pack('3s', '   '.encode())
    header_binary += struct.pack('I', date_as_int)
    header_binary += struct.pack('I', time_as_int)
    return header_binary


@dataclass
class FileParameters:
    path: str
    correct_datetime: datetime
    export_path: str


class SigmaRedactor:
    def __init__(self, file_parameter: FileParameters):
        self.file_parameter = file_parameter
        self.__origin_file_info = None
        self.__channels_count = None
        self.read_origin_header()

    def read_origin_header(self):
        bin_data = BinaryFile(file_path=self.file_parameter.path)
        self.__channels_count = bin_data.channels_count
        self.__origin_file_info = bin_data.short_file_info

    def read_origin_array(self) -> np.ndarray:
        bin_data = BinaryFile(file_path=self.file_parameter.path)
        signals = None
        for component in bin_data.record_type:
            signal = bin_data.read_signal(component)
            if signals is None:
                signals = signal
            else:
                signals = np.column_stack((signals, signal))
        return signals

    @property
    def channels_count(self) -> int:
        return self.__channels_count

    @property
    def origin_file_info(self) -> FileInfo:
        return self.__origin_file_info

    @property
    def new_header(self) -> bytes:
        return create_pseudo_sigma_header(
            channel_count=self.channels_count,
            datetime_start=self.file_parameter.correct_datetime,
            frequency=self.origin_file_info.frequency,
            longitude=self.origin_file_info.longitude,
            latitude=self.origin_file_info.latitude
        )

    def save(self):
        with open(self.file_parameter.export_path, 'wb') as file_ctx:
            file_ctx.write(self.new_header)
            self.read_origin_array().tofile(file_ctx)
