#!/usr/bin/env python3
"""Parses the FOURCC data in GPMF stream into fields"""
import construct

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
            print("{} {} > {}: {}".format(
                timestamps,
                ' > '.join([x.decode('ascii') for x in parents]),
                element.key.decode('ascii'),
                element.data
            ))
