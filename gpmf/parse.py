# TODO: Implement GPMF parsing
#   see https://github.com/gopro/gpmf-parser#gmfp-deeper-dive for format details
import construct

TYPES = construct.Enum(
    Byte,
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
    "data" / construct.Aligned(4, construct.Bytes(this.size * this.repeat))
)
