# encoding: utf-8

import os
from static_bundle.utils import prepare_path


class AbstractPath(object):
    """
    Base path type
    Provides methods for links collecting
    """

    def get_files(self):
        """
        Collect used files
        Return list with one element for single file
        and list with all files for directory path

        :rtype: list
        """
        raise NotImplementedError

    def get_abs_and_rel_paths(self, root_path, file_name, input_dir):
        """
        Return absolute and relative path for file

        :type root_path: str|unicode
        :type file_name: str|unicode
        :type input_dir: str|unicode
        :rtype: tuple

        """
        # todo: change relative path resolving [bug on duplicate dir names in path]
        relative_dir = root_path.replace(input_dir, '')
        return os.path.join(root_path, file_name), relative_dir + '/' + file_name


class FilePath(AbstractPath):
    """
    Path type for single file
    """

    def __init__(self, file_path, bundle=None):
        """
        :type file_path: str|unicode
        :type bundle: static_bundle.bundles.AbstractBundle
        """
        self.file_path = prepare_path(file_path)
        self.bundle = bundle

    def get_files(self):
        """
        :inheritdoc
        """
        assert self.bundle, 'Cannot fetch file name with empty bundle'
        abs_path, rel_path = self.get_abs_and_rel_paths(self.bundle.path, self.file_path, self.bundle.input_dir)
        file_cls = self.bundle.get_file_cls()
        return [file_cls(rel_path, abs_path)]


class DirectoryPath(AbstractPath):
    """
    :type directory_path: str|unicode
    :type bundle: static_bundle.bundles.AbstractBundle
    :type exclusions: list|None
    """

    def __init__(self, directory_path, bundle=None, exclusions=None):
        self.directory_path = prepare_path(directory_path)
        self.bundle = bundle
        self.exclusions = exclusions

    def get_files(self):
        """
        :inheritdoc
        """
        assert self.bundle, 'Cannot fetch directory name with empty bundle'
        result_files = []
        bundle_ext = self.bundle.get_extension()
        ext = "." + bundle_ext if bundle_ext else None
        if self.directory_path == "":
            root_path = self.bundle.path
        else:
            root_path = os.path.join(self.bundle.path, self.directory_path)
        for root, dirs, files in os.walk(root_path):
            for fpath in files:
                if (not ext or fpath.endswith(ext)) and (not self.exclusions or all(fpath != n for n in self.exclusions)):
                    abs_path, rel_path = self.get_abs_and_rel_paths(root, fpath, self.bundle.input_dir)
                    file_cls = self.bundle.get_file_cls()
                    result_files.append(file_cls(rel_path, abs_path))
        return result_files