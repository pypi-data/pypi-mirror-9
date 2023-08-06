"""Resource management methods."""
import sys
import os
import re
import zipfile
import tarfile
import six
from six.moves import urllib
from .support import Path
from .archive import IArchive, Archive, UnrecognizedArchiveFormat

__all__ = ["Resources"]


class FileObject(IArchive):

    def load(self, path):
        return Path(path)

    def filename(self):
        return self._archive

    def open(self, mode='rb'):
        return open(str(self._archive), mode=mode)


Archive.EXTENSION_MAP['.fileobject'] = FileObject


class Resources(object):
    """The Resources class manages a set of file resources and eases
    accessing them by using relative paths, scanning archives
    automatically and so on.
    """
    def __init__(self, searchpaths=None, excludepattern=None):
        """Creates a new resource container instance.

        For each searchpath provided, the resource container will scan the path
        and add all found files to itself, looking both at the filesystem and inside of archives.
        """
        if isinstance(searchpaths, basestring):
            searchpaths = [searchpaths]
        self.searchpaths = list(searchpaths)
        self.files = {}
        for path in self.searchpaths:
            self.scan(path, excludepattern)

    def _add(self, relpath, abspath):
        """Adds a file to the Resources container.

        Depending on the file type (determined by the file suffix or name),
        the file will be automatically scanned (if it is an archive) or
        checked for availability (if it is a stream/network resource).
        """        
        try:
            archive = Archive(abspath)
            for relpath in archive.files():
                archiveabspath = '{0}@{1}'.format(archive.filename(),
                                                  relpath)
                self._add_file(relpath,
                               archiveabspath,
                               archive)
        except UnrecognizedArchiveFormat:
            archive = Archive(abspath, ext='.FILEOBJECT')
            self._add_file(relpath, abspath, archive)

    def _add_file(self, relpath, abspath, archive=None):
        if relpath in self.files.keys():
            raise ValueError('clashing relative path names for:\n{0}\nand\n{1}'.format(abspath,
                                                                                       self.filename(relpath)))
        self.files[relpath] = (abspath, archive)

    def read(self, relpath):
        """Returns a string buffer for the given relative path.

        Raises a KeyError, if filename could not be found.
        """
        abspath, archive = self.files[relpath]
        return archive.read()

    def open(self, relpath):
        """Returns the file handle of the given relative path.
        If it is only available within an archive, a string buffer will be returned.

        Raises a KeyError, if filename could not be found.
        """
        abspath, archive = self.files[relpath]
        return archive.open()

    def get_filename(self, relpath):
        """Returns the absolute path of the given relative path.

        Raises a KeyError, if filename could not be found.
        """
        abspath, archive = self.files[relpath]
        return abspath

    def scan(self, path, excludepattern=None):
        """Scans a path and adds all found files to the Resources
        container.

        Scans a path and adds all found files to the Resources
        container. If a file is a supported (ZIP or TAR) archive, its
        contents will be indexed and added automatically.

        The method will consider the directory part (os.path.dirname) of
        the provided path as path to scan, if the path is not a
        directory.

        excludepattern can be a regular expression to skip directories, which
        match the pattern.
        """
        match = None
        if excludepattern:
            match = re.compile(excludepattern).match
        abspath = os.path.abspath(path)
        if not os.path.exists(abspath):
            raise ValueError("invalid path '%s'" % path)
        if not os.path.isdir(abspath):
            abspath = os.path.dirname(abspath)
        if not abspath.endswith(os.path.sep):
            abspath += os.path.sep
        if not os.path.exists(abspath):
            raise ValueError("invalid path '%s'" % path)
        for (dirpath, dirnames, filenames) in os.walk(abspath):
            if match and match(dirpath) is not None:
                continue
            for filename in filenames:
                absfilepath = os.path.join(dirpath, filename)
                relfilepath = absfilepath.replace(abspath, '')
                self._add(relfilepath, absfilepath)
