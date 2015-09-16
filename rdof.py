#!/usr/bin/env python
"""Remove duplicated object files

Usage: python rdof.py source target

Remove all object files contains in target from source and create a new source static library file in current directory.

Arguments:
    source  static library file to deal with
    target  static library file which contains object files to be removed

Example:
    rdof.py libcocos2d-x.a libssl.a     remove ssl from cocos2d-x
"""

import sys
import tempfile
import shutil
import subprocess

FAT_MAGIC = b'\xca\xfe\xba\xbe'


def usage():
    print __doc__


def is_fat(lib):
    with open(lib, 'rb') as f:
        header = f.read(4)
    return header == FAT_MAGIC


def get_obj_files(lib):
    def get_obj_files_from_thin_file(thin):
        results = {}
        output = subprocess.check_output(['ar', '-t', thin])
        for o in [f.strip() for f in output.split('\n') if f.endswith('.o')]:
            results[o] = True
        return results

    if is_fat(lib):
        obj_files = {}
        try:
            temp = tempfile.mkdtemp(dir='.')
            for arch in get_arches(lib):
                thin_file = "%s/%s.%s" % (temp, arch, lib)
                subprocess.check_call(['lipo', lib, '-thin', arch, '-o', thin_file])
                obj_files.update(get_obj_files_from_thin_file(thin_file))
        finally:
            shutil.rmtree(temp)

        print 'Get obj files from', lib, ':', obj_files.keys()
        return obj_files
    else:
        files = get_obj_files_from_thin_file(lib)
        print 'Get obj files from', lib, ':', files.keys()
        return files


def get_arches(static_lib):
    info = subprocess.check_output(['lipo', '-info', static_lib])
    arches = info.split(':')[-1].split()
    print 'Arches of', static_lib, ':', arches
    return arches


def delete_obj_files(source, obj_files):
    files = get_obj_files(source).keys()
    files_to_delete = []
    for f in files:
        if f not in obj_files:
            continue
        files_to_delete.append(f)

    print 'Delete', files_to_delete, 'from', source
    subprocess.check_call(['ar', '-d', source] + files_to_delete)


def remove_target_from_source(source, target):
    removes = get_obj_files(target)

    if not is_fat(source):
        delete_obj_files(source, removes)
        return

    temp = tempfile.mkdtemp(dir='.')
    thin_files = []

    try:
        for arch in get_arches(source):
            thin_file = "%s/%s.%s" % (temp, arch, source)
            thin_files.append(thin_file)

            subprocess.check_call(['lipo', source, '-thin', arch, '-o', thin_file])

            delete_obj_files(thin_file, removes)

        print 'Done, create %s' % ('new.' + source)
        command = ['lipo', '-create'] + thin_files + ['-o', 'new.' + source]
        subprocess.check_call(command)
    finally:
        shutil.rmtree(temp)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage()
        sys.exit(2)

    remove_target_from_source(sys.argv[1], sys.argv[2])

