#!/usr/bin/env python3
import hachoir.metadata
import hachoir.parser


from hachoir.field import MissingField
from hachoir.field.string_field import String

def get_file_metadata(filepath):
    """Parse and extract metadata with hachoir"""
    parser = hachoir.parser.createParser(filepath)
    with parser:
        md = hachoir.metadata.extractMetadata(parser)
    return md


def get_raw_content(met):
    """Reads the raw bytes from the stream for this atom/field"""
    if hasattr(met, 'stream'):
        stream = met.stream
    else:
        stream = met.parent.stream
    return stream.read(met.absolute_address, met.size)


def get_payloads(stbl):
    """Get raw payload(s) from stbl atom offsets"""
    ret_bytes = b''
    for subatom in stbl:
        tag = subatom['tag']
        if tag.value == 'stsz':
            stsz = subatom
        if tag.value == 'stco':
            stco = subatom
    num_samples = stsz['stsz/count'].value
    for x in range(num_samples):
        offset = stco["stco/chunk_offset[{}]".format(x)].value
        size = stsz["stsz/sample_size[{}]".format(x)].value
        resp = stbl.stream.read(offset, size)
        ret_bytes += resp[1]
    return ret_bytes


def find_gpmd_stbl_atom(parser):
    """Find the stbl atom"""
    minf_atom = find_gpmd_minf_atom(parser)
    if not minf_atom:
        return None
    try:
        for minf_field in minf_atom:
            tag = minf_field['tag']
            if tag.value != 'stbl':
                continue
            return minf_field['stbl']
    except MissingField:
        pass


def find_gpmd_minf_atom(parser):
    """Find minf atom for GPMF media"""
    def recursive_search(atom):
        try:
            subtype = atom['hdlr/subtype']
            if subtype.value == 'meta':
                meta_atom = atom.parent
                #print(meta_atom)
                for subatom in meta_atom:
                    tag = subatom['tag']
                    if tag.value != 'minf':
                        continue
                    minf_atom = subatom['minf']
                    #print("  {}".format(minf_atom))
                    for minf_field in minf_atom:
                        tag = minf_field['tag']
                        #print("    {}".format(tag))
                        if tag.value != 'gmhd':
                            continue
                        if b'gpmd' in minf_field['data'].value:
                            return minf_atom
        except MissingField:
            pass
        try:
            for x in atom:
                ret = recursive_search(x)
                if ret:
                    return ret
        except KeyError as e:
            pass
        return None
    return recursive_search(parser)


def recursive_print(input):
    """Recursively print hachoir parsed state"""
    print(repr(input))
    if isinstance(input, String):
        print("  {}".format(input.display))
    try:
        for x in input:
            recursive_print(x)
    except KeyError as e:
        pass


if __name__ == '__main__':
    import sys
    parser = hachoir.parser.createParser(sys.argv[1])
    with open(sys.argv[2], 'wb') as fp:
        fp.write(
            get_payloads(
                find_gpmd_stbl_atom(parser)
            )
        )
