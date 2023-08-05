# encoding: utf-8

import os
import shutil
import codecs


def prepare_path(path):
    """
    Path join helper method
    Join paths if list passed

    :type path: str|unicode|list
    :rtype: str|unicode
    """
    if type(path) == list:
        return os.path.join(*path)
    return path


def read_from_file(file_path, encoding="utf-8"):
    """
    Read helper method

    :type file_path: str|unicode
    :type encoding: str|unicode
    :rtype: str|unicode
    """
    with codecs.open(file_path, "r", encoding) as f:
        return f.read()


def write_to_file(file_path, contents, encoding="utf-8"):
    """
    Write helper method

    :type file_path: str|unicode
    :type contents: str|unicode
    :type encoding: str|unicode
    """
    with codecs.open(file_path, "w", encoding) as f:
        f.write(contents)


def copy_file(src, dest):
    """
    Copy file helper method

    :type src: str|unicode
    :type dest: str|unicode
    """
    dir_path = os.path.dirname(dest)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    shutil.copy2(src, dest)


def get_path_extension(path):
    """
    Split file name and extension

    :type path: str|unicode
    :rtype: one str|unicode
    """
    file_path, file_ext = os.path.splitext(path)
    return file_ext.lstrip('.')


def split_path(path):
        """
        Helper method for absolute and relative paths resolution
        Split passed path and return each directory parts

        example: "/usr/share/dir"
        return: ["usr", "share", "dir"]

        @type path: one of (unicode, str)
        @rtype: list
        """
        result_parts = []
        #todo: check loops
        while path != "/":
            parts = os.path.split(path)
            if parts[1] == path:
                result_parts.insert(0, parts[1])
                break
            elif parts[0] == path:
                result_parts.insert(0, parts[0])
                break
            else:
                path = parts[0]
                result_parts.insert(0, parts[1])
        return result_parts