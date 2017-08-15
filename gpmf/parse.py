#!/usr/bin/env python3
"""Parses the FOURCC data in GPMF stream into fields"""
import construct
import dateutil.parser

TYPES = construct.Enum(
    construct.Byte,
    int8_t=ord(b'b'),
    uint8_t=ord(b'B'),
    char=ord(b'c'),
    int16_t=ord(b's'),
    uint16_t=ord(b'S'),
    int32_t=ord(b'l'),
    uint32_t=ord(b'L'),
    float=ord(b'f'),
    double=ord(b'd'),
    fourcc=ord(b'F'),
    uuid=ord(b'G'),
    int64_t=ord(b'j'),
    uint64_t=ord(b'J'),
    Q1516=ord(b'q'),
    Q3132=ord(b'Q'),
    utcdate=ord(b'U'),
    complex=ord(b'?'),
    nested=0x0,
)

FOURCC = construct.Struct(
    "key" / construct.Bytes(4),
    "type" / construct.Byte,
    "size" / construct.Byte,
    "repeat" / construct.Int16ub,
    "data" / construct.Aligned(4, construct.Bytes(construct.this.size * construct.this.repeat))
)


def parse_value(element):
    """Parses element value"""
    type_parsed = TYPES.parse(bytes([element.type]))
    raise ValueError("{} does not have value parser yet".format(type_parsed))


def parse_goprodate(element):
    """Parses the gopro date string from element to Python datetime"""
    goprotime = element.data.decode('UTF-8')
    return dateutil.parser.parse("{}-{}-{}T{}:{}:{}Z".format(
        2000 + int(goprotime[:2]),  # years
        int(goprotime[2:4]),        # months
        int(goprotime[4:6]),        # days
        int(goprotime[6:8]),        # hours
        int(goprotime[8:10]),       # minutes
        float(goprotime[10:])       # seconds
    ))


def recursive(data, parents=tuple()):
    """Recursive parser returns depth-first traversing generator yielding fields and list of their parent keys"""
    elements = FOURCC[:].parse(data)
    for element in elements:
        if element.type == 0:
            subparents = parents + (element.key,)
            for subyield in recursive(element.data, subparents):
                yield subyield
        else:
            yield (element, parents)


if __name__ == '__main__':
    import sys
    from extract import get_gpmf_payloads_from_file
    payloads, parser = get_gpmf_payloads_from_file(sys.argv[1])
    for gpmf_data, timestamps in payloads:
        for element, parents in recursive(gpmf_data):
            try:
                if element.key == b'GPSU':
                    value = parse_goprodate(element)
                else:
                    value = parse_value(element)
            except ValueError:
                value = element.data
            print("{} {} > {}: {}".format(
                timestamps,
                ' > '.join([x.decode('ascii') for x in parents]),
                element.key.decode('ascii'),
                value
            ))
