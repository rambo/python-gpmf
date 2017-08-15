#!/usr/bin/env python3
import datetime
import shutil

import gpmf.extract
import gpmf.parse
import hachoir.editor
import hachoir.parser
import hachoir.stream
from hachoir.field import MissingField


def locate_fields_by_subpath(parser, subpath):
    """Locate mp4 fields by their subpath element name"""
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


def fix_file_timestamp(filepath, overwrite=False, sanity_year=None):
    """Fixed mp4 file metadata timestamps to GPS clock (if available)"""
    newpath = filepath + '.new'
    payloads, parser = gpmf.extract.get_gpmf_payloads_from_file(filepath)
    have_fix = False
    starttime = None

    for gpmf_data, timestamps in payloads:
        for element, parents in gpmf.parse.recursive(gpmf_data):
            if element.key == b'GPSF' and gpmf.parse.parse_value(element) > 0:
                have_fix = True
            if have_fix and element.key == b'GPSU':
                gpstime = gpmf.parse.parse_value(element)
                starttime = gpstime - datetime.timedelta(seconds=timestamps[0] / 1000)
                break

    if not starttime:
        print("ERROR: No GPS fix/time found")
        return False

    if sanity_year:
        if sanity_year != starttime.year:
            print("ERROR: Sanity mismatch {} != {}".format(starttime.year, sanity_year))
            return False

    # We happen to know this is always in UTC so we can just drop the tzinfo
    starttime_naive = starttime.replace(tzinfo=None)

    # Create editor and adjust timestamps
    editor = hachoir.editor.createEditor(parser)
    changed = False
    for atom in locate_fields_by_subpath(parser, 'creation_date'):
        cd = editor[atom.path]
        if cd.value == starttime_naive:
            continue
        cd.value = starttime_naive
        changed = True

    if not changed:
        print("INFO: Nothing was changed")
        return True

    # Write the changed data
    output = hachoir.stream.FileOutputStream(newpath)
    with output:
        editor.writeInto(output)

    if overwrite:
        shutil.move(newpath, filepath)

    return True


if __name__ == '__main__':
    import sys
    overwrite = False
    if len(sys.argv) > 2:
        overwrite = bool(int(sys.argv[2]))
    sanity_year = None
    if len(sys.argv) > 3:
        sanity_year = int(sys.argv[3])

    result = fix_file_timestamp(sys.argv[1], overwrite, sanity_year)
    if not result:
        sys.exit(1)
