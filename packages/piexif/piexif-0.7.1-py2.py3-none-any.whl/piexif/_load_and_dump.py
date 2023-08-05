import copy
import io
import struct
import sys

from ._common import *
from ._exif import *


if sys.version_info[0] == 2:
    NUMBER_TYPE = (int, long)
else:
    NUMBER_TYPE = int


TYPES = {
    "Byte": 1,
    "Ascii": 2,
    "Short": 3,
    "Long": 4,
    "Rational": 5,
    "Undefined": 7,
    "SLong": 9,
    "SRational": 10}


POINTERS = (34665, 34853)

LITTLE_ENDIAN = b"\x49\x49"

TIFF_HEADER_LENGTH = 8

BYTE_LENGTH = 1
SHORT_LENGTH = 2
LONG_LENGTH = 4


class ExifReader(object):
    EXT = (b".jpg", b"jpeg", b".jpe", b".tif", b"tiff")

    def __init__(self, data):
        if data[0:2] in (b"\xff\xd8", b"\x49\x49", b"\x4d4d"):
            pass
        elif data[-4:].lower().encode() in self.EXT:
            with open(data, 'rb') as f:
                data = f.read()
        else:
            raise ValueError("Given file is neither JPEG nor TIFF.")

        if data[0:2] == b"\xff\xd8":
            segments = split_into_segments(data)
            app1 = get_app1(segments)

            if app1:
                self.exif_str = app1[10:]
            else:
                self.exif_str = None
        elif data[0:2] in (b"\x49\x49", b"\x4d4d"):
            self.exif_str = data
        else:
            raise ValueError("Given file is neither JPEG nor TIFF.")

    def get_exif_ifd(self):
        if self.exif_str is None:
            raise ValueError("exif_str is empty.")
        exif_dict = {}
        gps_dict = {}

        if self.exif_str[0:2] == LITTLE_ENDIAN:
            self.endian_mark = "<"
        else:
            self.endian_mark = ">"
        pointer = struct.unpack(self.endian_mark + "L", self.exif_str[4:8])[0]
        zeroth_dict = self.get_ifd_dict(pointer)

        if 34665 in zeroth_dict:
            pointer = struct.unpack(self.endian_mark + "L",
                                    zeroth_dict[34665][2])[0]
            exif_dict = self.get_ifd_dict(pointer)

        if 34853 in zeroth_dict:
            pointer = struct.unpack(self.endian_mark + "L",
                                    zeroth_dict[34853][2])[0]
            gps_dict = self.get_ifd_dict(pointer)

        return zeroth_dict, exif_dict, gps_dict

    def get_ifd_dict(self, pointer):
        ifd_dict = {}
        tag_count = struct.unpack(self.endian_mark + "H",
                                  self.exif_str[pointer: pointer+2])[0]
        offset = pointer + 2
        for x in range(tag_count):
            pointer = offset + 12 * x
            tag_code = struct.unpack(self.endian_mark + "H",
                       self.exif_str[pointer: pointer+2])[0]
            value_type = struct.unpack(self.endian_mark + "H",
                         self.exif_str[pointer + 2: pointer + 4])[0]
            value_num = struct.unpack(self.endian_mark + "L",
                                      self.exif_str[pointer + 4: pointer + 8]
                                      )[0]
            value = self.exif_str[pointer+8: pointer+12]
            ifd_dict.update({tag_code:[value_type, value_num, value]})

#            # any length number value
#            if (value_type in (1, 3, 4, 9)) and (value_num > 1):
#                print(tag_code, value_type, value_num, value)
        return ifd_dict

    def get_info(self, val):
        data = None
        t = val[0]
        length = val[1]
        value = val[2]

        if t == 1: # BYTE
            if length > 4:
                pointer = struct.unpack(self.endian_mark + "L", value)[0]
                data = struct.unpack("B" * length,
                                     self.exif_str[pointer: pointer + length])
            else:
                data = struct.unpack("B" * length, value[0:length])
        elif t == 2: # ASCII
            if length > 4:
                pointer = struct.unpack(self.endian_mark + "L", value)[0]
                data = self.exif_str[pointer: pointer+length - 1]
            else:
                data = value[0: length - 1]
            try:
                data = data.decode()
            except:
                pass
        elif t == 3: # SHORT
            if length > 2:
                pointer = struct.unpack(self.endian_mark + "L", value)[0]
                data = struct.unpack(self.endian_mark + "H" * length,
                                     self.exif_str[pointer: pointer+length*2])
            else:
                data = struct.unpack(self.endian_mark + "H" * length,
                                     value[0:length * 2])
        elif t == 4: # LONG
            if length > 1:
                pointer = struct.unpack(self.endian_mark + "L", value)[0]
                data = struct.unpack(self.endian_mark + "L" * length,
                                     self.exif_str[pointer: pointer+length*4])
            else:
                data = struct.unpack(self.endian_mark + "L" * length,
                                     value)
        elif t == 5: # RATIONAL
            pointer = struct.unpack(self.endian_mark + "L", value)[0]
            if length > 1:
                data = tuple(
                    (struct.unpack(self.endian_mark + "L",
                                   self.exif_str[pointer + x * 8:
                                       pointer + 4 + x * 8])[0],
                     struct.unpack(self.endian_mark + "L",
                                   self.exif_str[pointer + 4 + x * 8:
                                       pointer + 8 + x * 8])[0])
                    for x in range(length)
                )
            else:
                data = (struct.unpack(self.endian_mark + "L",
                                      self.exif_str[pointer: pointer + 4])[0],
                        struct.unpack(self.endian_mark + "L",
                                      self.exif_str[pointer + 4: pointer + 8]
                                      )[0])
        elif t == 7: # UNDEFINED BYTES
            if length > 4:
                pointer = struct.unpack(self.endian_mark + "L", value)[0]
                data = self.exif_str[pointer: pointer+length]
            else:
                data = value[0:length]
#        elif t == 9: # SLONG
#            if length > 1:
#                pointer = struct.unpack(self.endian_mark + "L", value)[0]
#                data = struct.unpack(self.endian_mark + "l" * length,
#                                     self.exif_str[pointer: pointer+length*4])
#            else:
#                data = struct.unpack(self.endian_mark + "l" * length,
#                                     value)
        elif t == 10: # SRATIONAL
            pointer = struct.unpack(self.endian_mark + "L", value)[0]
            if length > 1:
                data = tuple(
                  (struct.unpack(self.endian_mark + "l",
                    self.exif_str[pointer + x * 8: pointer + 4 + x * 8])[0],
                   struct.unpack(self.endian_mark + "l",
                    self.exif_str[pointer + 4 + x * 8: pointer + 8 + x * 8])[0])
                  for x in range(length)
                )
            else:
                data = (struct.unpack(self.endian_mark + "l",
                                      self.exif_str[pointer: pointer + 4])[0],
                        struct.unpack(self.endian_mark + "l",
                                      self.exif_str[pointer + 4: pointer + 8]
                                      )[0])
        else:
            raise ValueError("Exif might be wrong. Got incorrect value " +
                             "type to decode.")

        if isinstance(data, tuple) and (len(data) == 1):
            return data[0]
        else:
            return data


def load(input_data):
    r"""
    py:function:: piexif.load(filename)

    Return three IFD data that are 0thIFD, ExifIFD, and GPSIFD as dict.

    :param str filename: JPEG or TIFF
    :return: 0th IFD, Exif IFD, and GPS IFD
    :rtype: dict, dict, dict
    """
    exifReader = ExifReader(input_data)
    if exifReader.exif_str is None:
        return {}, {}, {}
    zeroth_ifd, exif_ifd, gps_ifd = exifReader.get_exif_ifd()
    zeroth_dict = {key: exifReader.get_info(zeroth_ifd[key])
                   for key in zeroth_ifd if key in TAGS["Zeroth"]}
    exif_dict = {key: exifReader.get_info(exif_ifd[key])
                 for key in exif_ifd if key in TAGS["Exif"]}
    gps_dict = {key: exifReader.get_info(gps_ifd[key])
                for key in gps_ifd if key in TAGS["GPSInfo"]}

    return zeroth_dict, exif_dict, gps_dict


def dump(zeroth_ifd_original, exif_ifd={}, gps_ifd={}):
    """
    py:function:: piexif.load(data)

    Return three IFD data that are 0thIFD, ExifIFD, and GPSIFD as dict.

    :param bytes data: JPEG or TIFF
    :return: 0th IFD, Exif IFD, and GPS IFD
    :rtype: dict, dict, dict
    """
    zeroth_ifd = copy.deepcopy(zeroth_ifd_original)
    header = b"\x45\x78\x69\x66\x00\x00\x4d\x4d\x00\x2a\x00\x00\x00\x08"
    exif_is = False
    gps_is = False
    if len(exif_ifd):
        zeroth_ifd.update({34665: 1})
        exif_is = True
    if len(gps_ifd):
        zeroth_ifd.update({34853: 1})
        gps_is = True

    zeroth_set = dict_to_bytes(zeroth_ifd, "Zeroth", 0)
    zeroth_length = (len(zeroth_set[0]) + exif_is * 12 + gps_is * 12 +
                     4 + len(zeroth_set[1]))

    if exif_is:
        exif_set = dict_to_bytes(exif_ifd, "Exif", zeroth_length)
        exif_bytes = b"".join(exif_set)
        exif_length = len(exif_bytes)
    else:
        exif_bytes = b""
        exif_length = 0
    if gps_is:
        gps_set = dict_to_bytes(gps_ifd, "GPSInfo", zeroth_length + exif_length)
        gps_bytes = b"".join(gps_set)
        gps_length = len(gps_bytes)
    else:
        gps_bytes = b""
        gps_length = 0

    if exif_is:
        pointer_value = TIFF_HEADER_LENGTH + zeroth_length
        pointer_str = struct.pack(">I", pointer_value)
        key = 34665
        key_str = struct.pack(">H", key)
        type_str = struct.pack(">H", TYPES["Long"])
        length_str = struct.pack(">I", 1)
        exif_pointer = key_str + type_str + length_str + pointer_str
    else:
        exif_pointer = b""
    if gps_is:
        pointer_value = TIFF_HEADER_LENGTH + zeroth_length + exif_length
        pointer_str = struct.pack(">I", pointer_value)
        key = 34853
        key_str = struct.pack(">H", key)
        type_str = struct.pack(">H", TYPES["Long"])
        length_str = struct.pack(">I", 1)
        gps_pointer = key_str + type_str + length_str + pointer_str
    else:
        gps_pointer = b""
    zeroth_bytes = (zeroth_set[0] + exif_pointer + gps_pointer +
                    b"\x00\x00\x00\x00" + zeroth_set[1])

    return header + zeroth_bytes + exif_bytes + gps_bytes


def pack_byte(*args):
    return struct.pack("B" * len(args), *args)


def pack_short(*args):
    return struct.pack(">" + "H" * len(args), *args)


def pack_long(*args):
    return struct.pack(">" + "L" * len(args), *args)


def pack_slong(*args):
    return struct.pack(">" + "l" * len(args), *args)


def dict_to_bytes(ifd_dict, group, ifd_offset):
    exif_ifd_is = False
    gps_ifd_is = False
    tag_count = len(ifd_dict)
    entry_header = struct.pack(">H", tag_count)
    if group == "Zeroth":
        entries_length = 2 + tag_count * 12 + 4
    else:
        entries_length = 2 + tag_count * 12
    entries = b""
    values = b""

    for n, key in enumerate(sorted(ifd_dict)):
        if key == 34665:
            exif_ifd_is = True
            continue
        elif key == 34853:
            gps_ifd_is = True
            continue

        raw_value = ifd_dict[key]
        key_str = struct.pack(">H", key)
        value_type = TAGS[group][key]["type"]
        type_str = struct.pack(">H", TYPES[value_type])
        four_bytes_over = b""

        if isinstance(raw_value, NUMBER_TYPE):
            raw_value = (raw_value,)

        if value_type == "Byte":
            length = len(raw_value)
            if length <= 4:
                value_str = (pack_byte(*raw_value) +
                             b"\x00" * (4 - length))
            else:
                offset = (TIFF_HEADER_LENGTH + ifd_offset +
                          entries_length + len(values))
                value_str = struct.pack(">I", offset)
                four_bytes_over = pack_byte(*raw_value)
        elif value_type == "Short":
            length = len(raw_value)
            if length <= 2:
                value_str = (pack_short(*raw_value) +
                             b"\x00\x00" * (2 - length))
            else:
                offset = (TIFF_HEADER_LENGTH + ifd_offset +
                          entries_length + len(values))
                value_str = struct.pack(">I", offset)
                four_bytes_over = pack_short(*raw_value)
        elif value_type == "Long":
            length = len(raw_value)
            if length <= 1:
                value_str = pack_long(*raw_value)
            else:
                offset = (TIFF_HEADER_LENGTH + ifd_offset +
                          entries_length + len(values))
                value_str = struct.pack(">I", offset)
                four_bytes_over = pack_long(*raw_value)
#        elif value_type == "SLong":
#            length = len(raw_value)
#            if length <= 1:
#                value_str = pack_long(*raw_value)
#            else:
#                offset = (TIFF_HEADER_LENGTH + ifd_offset +
#                          entries_length + len(values))
#                value_str = struct.pack(">I", offset)
#                four_bytes_over = pack_slong(*raw_value)
        elif value_type == "Ascii":
            new_value = raw_value.encode() + b"\x00"
            length = len(new_value)
            if length > 4:
                offset = (TIFF_HEADER_LENGTH + ifd_offset +
                          entries_length + len(values))
                value_str = struct.pack(">I", offset)
                four_bytes_over = new_value
            else:
                value_str = new_value + b"\x00" * (4 - length)
        elif value_type == "Rational":
            if isinstance(raw_value[0], NUMBER_TYPE):
                length = 1
                num, den = raw_value
                new_value = struct.pack(">L", num) + struct.pack(">L", den)
            elif isinstance(raw_value[0], tuple):
                length = len(raw_value)
                new_value = b""
                for n, val in enumerate(raw_value):
                    num, den = val
                    new_value += struct.pack(">L", num) + struct.pack(">L", den)
            offset = (TIFF_HEADER_LENGTH + ifd_offset +
                      entries_length + len(values))
            value_str = struct.pack(">I", offset)
            four_bytes_over = new_value
        elif value_type == "SRational":
            if isinstance(raw_value[0], NUMBER_TYPE):
                length = 1
                num, den = raw_value
                new_value = struct.pack(">l", num) + struct.pack(">l", den)
            elif isinstance(raw_value[0], tuple):
                length = len(raw_value)
                new_value = b""
                for n, val in enumerate(raw_value):
                    num, den = val
                    new_value += struct.pack(">l", num) + struct.pack(">l", den)
            offset = (TIFF_HEADER_LENGTH + ifd_offset +
                      entries_length + len(values))
            value_str = struct.pack(">I", offset)
            four_bytes_over = new_value
        elif value_type == "Undefined":
            length = len(raw_value)
            if length > 4:
                offset = (TIFF_HEADER_LENGTH + ifd_offset +
                          entries_length + len(values))
                value_str = struct.pack(">I", offset)
                four_bytes_over = raw_value
            else:
                value_str = raw_value + b"\x00" * (4 - length)

        length_str = struct.pack(">I", length)
        entries += key_str + type_str + length_str + value_str
        values += four_bytes_over
    return (entry_header + entries, values)