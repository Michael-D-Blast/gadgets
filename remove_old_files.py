#! /usr/bin/env python

import os, sys
import shutil
import re
import time, datetime

class File :
    def __init__(self, file, mtime, type) :
        self._file = file
        self._mtime = mtime
        self._type = type

    @property
    def file(self) :
        return self._file

    @property
    def type(self) :
        return self._type

def get_file_type(file) :
    if os.path.isfile(file) :
        return 'file'
    elif os.path.isdir(file) :
        return 'dir'
    elif os.path.islink(file) :
        return 'link'
    else :
        raise Exception('Can not get file type!')

class FileFilter(object) :
    def __init__(self, pattern, path, seconds, type, debug = False) :
        if not os.path.isdir(path) :
            raise Exception(str(path) + ' does not exist!')

        self._now = time.time()

        self._path = path

        if pattern :
            self._pattern_specified = True
            self._pattern = re.compile(pattern)
        else :
            self._pattern_specified = False

        self._timedelta = seconds

        self._type = type

        self._debug = debug

        self._files_found = []

    def find_result(self) :
        for file in os.listdir(self._path) :
            if self._pattern_specified and self._pattern.search(file) :

                file_real_path = os.path.realpath(os.path.join(self._path, file))
                file_mtime = os.path.getmtime(file_real_path)

                if self._now - self._timedelta > file_mtime :

                    file_type = get_file_type(file_real_path)

                    if self._type == file_type or self._type == 'all' :

                        if self._debug : print(file_real_path, file_mtime, file_type)

                        if file_real_path != os.path.realpath(sys.argv[0]) :
                            self._files_found.append(File(file_real_path, file_mtime, file_type))
                        else :
                            if self._debug :
                                print(file_real_path)
                                print(os.path.realpath(sys.argv[0]))
                            raise Exception('I should remove myself!')

        return self._files_found

def remove_file_according_to_type(file) :
    if os.path.exists(file.file) :
        if file.type == 'file' :
            os.remove(file.file)
        elif file.type == 'dir' :
            shutil.rmtree(file.file)
        elif file.type == 'link' :
            os.unlink(file.file)
        else :
            raise Exception('Unknown type!')

        print('Removing ' + str(file.file))


class FileRemover(FileFilter) :
    def __init__(self, pattern, path, seconds, type, debug = False) :
        super(FileRemover, self).__init__(pattern, path, seconds, type, debug)

    def remove(self) :
        self.find_result()

        if self._files_found :
            for file in self._files_found :
                remove_file_according_to_type(file)

if __name__ == "__main__" :
    import argparse

    parser = argparse.ArgumentParser(description=\
            'Delete the files/directories matching the re patten and older than the time(in sec) you specify')
    parser.add_argument('--pattern', action='store', \
            help='Specify the regular exp pattern which the files or directories will be removed if match')
    parser.add_argument('--path', action='store', default='.', \
            help='Specify the path where to find the matched files, supporting relative path')
    parser.add_argument('-s', '--seconds', type=int, required=True, \
            action='store', help='The files/dirs N seconds older than now will be removed')
    parser.add_argument('-t', '--type', choices=['file', 'dir', 'symlink', 'all'], default='all', \
            action='store', help='Specify the kind of files that you want to remove')
    parser.add_argument('-d', '--debug', action='store_true', default=False, help='Enable debug information')
    # The option -f is only used for debug
#    parser.add_argument('-f', '--file', action='store', \
#            help='specify the file and check if it matches the pattern, used for testing the matching function')
    
    args = parser.parse_args()

    file_remover = FileRemover(pattern = args.pattern, path = args.path, seconds = args.seconds, type = args.type, debug = args.debug)

    file_remover.remove()

