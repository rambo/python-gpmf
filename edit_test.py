#!/usr/bin/env python3
import datetime

import hachoir.parser
import hachoir.editor
import hachoir.stream
from hachoir.field import MissingField


def locate_fields_by_subpath(parser, subpath):
    def recursive_search(atom, retlist=[]):
        try:
            cd = atom[subpath]
            retlist.append(cd)
        except MissingField:
            pass
        try:
            for x in atom:
                retlist = recursive_search(x, retlist)
        except KeyError as e:
            pass
        return retlist
    return recursive_search(parser)

def locate_creation_date_fields(parser):
    return locate_fields_by_subpath(parser, 'creation_date')


if __name__ == '__main__':
    import sys
    parser = hachoir.parser.createParser(sys.argv[1])
    editor = hachoir.editor.createEditor(parser)
    output = hachoir.stream.FileOutputStream(sys.argv[2])

    for atom in locate_creation_date_fields(parser):
        cd = editor[atom.path]
        cd.value = datetime.datetime.utcnow()

    with output:
        editor.writeInto(output)
