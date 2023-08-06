import os
from .common import split_path

__all__ = ['FileFinder']


class FileFinder(object):
    """
    Utility class to help find files from a given path
    It will search the current working directory to find the file then
    it will move on to searching within the given searchpaths at class instanciation
    """

    def __init__(self, searchpaths):
        if isinstance(searchpaths, basestring):
            searchpaths = [searchpaths]
        self.searchpaths = list(searchpaths)

    def find_file(self, template):
        if os.path.isabs(template):
            return template

        filename = os.path.abspath(template)
        if os.path.exists(filename):
            return filename

        _, parts = split_path(template)
        for searchpath in self.searchpaths:
            filename = os.path.join(searchpath, *parts)
            if not os.path.exists(filename):
                continue
            return filename

        # If we made it here we didn't find any file matches
        raise Exception('No file found for "{0}"'.format(template))
