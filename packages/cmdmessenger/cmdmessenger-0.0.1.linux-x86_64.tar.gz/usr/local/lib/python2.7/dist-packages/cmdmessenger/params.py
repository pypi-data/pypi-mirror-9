#!/usr/bin/env python
"""

'to': to arduino (python -> arduino)
'from': from arduino (arduino -> python)

types:
    bool
    int16
    int32
    float (can be scientific notation)
    floatsci
    double
    doublesci
    char
    string

    bbool (as bytes)
    bint16
    bint32
    bfloat
    bdouble
    bchar
"""

import struct

bool_to_string = lambda v: str(int(v))
bool_from_string = lambda s: bool(s)
bool_to_bytes = lambda v: struct.pack('<?', v)
bool_from_bytes = lambda s: struct.unpack('<?', s)

int16_to_string = lambda v: str(int(v) & 0xFFFF)
int16_from_string = lambda s: int(s)
int16_to_bytes = lambda v: struct.pack('<h', v & 0xFFFF)
int16_from_bytes = lambda s: struct.unpack('<h', s)

int32_to_string = lambda v: str(int(v) & 0xFFFFFFFF)
int32_from_string = lambda s: int(s)
int32_to_bytes = lambda v: struct.pack('<i', v & 0xFFFFFFFF)
int32_from_bytes = lambda s: struct.unpack('<i', s)

float_to_string = lambda v: str(float(v))  # TODO precision?
float_from_string = lambda s: float(s)
float_to_bytes = lambda v: struct.pack('<f', v)
float_from_bytes = lambda s: struct.unpack('<f', s)

floatsci_to_string = lambda v: '%E' % v
floatsci_from_string = lambda s: float(s)
#floatsci_to_bytes =
#floatsci_from_bytes =

doublesci_to_string = lambda v: '%E' % v
doublesci_from_string = lambda s: float(s)
#doublesci_to_bytes =
#doublesci_from_bytes =

double_to_string = lambda v: str(float(v))
double_from_string = lambda s: float(s)
double_to_bytes = lambda v: struct.pack('<d', v)
double_from_bytes = lambda s: struct.unpack('<f', s)

char_to_string = lambda v: v[0]
char_from_string = lambda s: s[0]
#char_to_bytes = lambda v: v[0]
#char_from_bytes = lambda s: s[0]

string_to_string = lambda v: v
string_from_string = lambda s: s
#string_to_bytes = lambda v: v
#string_from_bytes = lambda s: s


types = {
    'bool':  {'to': bool_to_string, 'from': bool_from_string},
    'int16': {'to': int16_to_string, 'from': int16_from_string},
    'int32': {'to': int32_to_string, 'from': int32_from_string},
    'float': {'to': float_to_string, 'from': float_from_string},
    'double': {'to': double_to_string, 'from': double_from_string},
    'char': {'to': char_to_string, 'from': char_from_string},
    'string': {'to': string_to_string, 'from': string_from_string},
    'float_sci': {'to': floatsci_to_string, 'from': floatsci_from_string},
    'double_sci': {'to': doublesci_to_string, 'from': doublesci_from_string},
    # bytes
    'byte_bool': {'to': bool_to_bytes, 'from': bool_from_bytes},
    'byte_int16': {'to': int16_to_bytes, 'from': int16_from_bytes},
    'byte_int32': {'to': int32_to_bytes, 'from': int32_from_bytes},
    'byte_float': {'to': float_to_bytes, 'from': float_from_bytes},
    'byte_double': {'to': double_to_bytes, 'from': double_from_bytes},
}

# add shortcuts
types['b'] = types['bool']
types['i'] = types['int16']
types['i16'] = types['int16']
types['i32'] = types['int32']
types['f'] = types['float']
types['d'] = types['double']
types['c'] = types['char']
types['s'] = types['string']
types['fs'] = types['float_sci']

types['ds'] = types['double_sci']
types['bb'] = types['byte_bool']
types['bi'] = types['byte_int16']
types['bi16'] = types['byte_int16']
types['bi32'] = types['byte_int32']
types['bf'] = types['byte_float']
types['bd'] = types['byte_double']

types[bool] = types['bool']
types[int] = types['int16']
types[float] = types['float']
types[str] = types['string']
