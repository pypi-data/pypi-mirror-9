import os
import tarfile
import zipfile
import six

__all__ = ['Archive',
           'extract',
           'ArchiveException', 'UnrecognizedArchiveFormat', 'UnsafeArchive']


class ArchiveException(Exception):
    """Base exception class for all archive errors."""


class UnrecognizedArchiveFormat(ArchiveException):
    """Error raised when passed file is not a recognized archive format."""


class UnsafeArchive(ArchiveException):
    """
    Error raised when passed file contains paths that would be extracted
    outside of the target directory.
    """


def extract(path, to_path='', ext='', **kwargs):
    """
    Unpack the tar or zip file at the specified path to the directory
    specified by to_path.
    """
    Archive(path, ext=ext).extract(to_path, **kwargs)


class IArchive(object):
    """The interface that is shared between the common Archive class and
    all of its specific encapsulations IE TarArchive, ZipArchive"""
    def __init__(self, path):
        self._archive = self.load(path)

    def __del__(self):
        if hasattr(self, "_archive"):
            if hasattr(self._archive, 'close'):
                self._archive.close()

    def load(self, path):
        raise NotImplementedError()

    def list(self):
        raise NotImplementedError()

    def filename(self):
        raise NotImplementedError()

    def files(self):
        raise NotImplementedError()

    def open(self, *args, **kwargs):
        raise NotImplementedError()

    def read(self, *args, **kwargs):
        fh = self.open(*args, **kwargs)
        data = six.BytesIO(fh.read())
        fh.close()
        return data

    def extract(self, to_path):
        raise NotImplementedError()


class TarArchive(IArchive):

    def load(self, path):
        # tarfile's open uses different parameters for file path vs. file obj.
        if isinstance(path, six.string_types):
            return tarfile.open(name=path)
        else:
            return tarfile.open(fileobj=path)

    def filename(self):
        return self._archive.name

    def open(self, relpath):
        return self._archive.extractfile(relpath)

    def files(self):
        for path in self._archive.getnames():
            yield path

    def list(self, *args, **kwargs):
        self._archive.list(*args, **kwargs)


class ZipArchive(IArchive):

    def load(self, path):
        return zipfile.ZipFile(path)

    def filename(self):
        return self._archive.filename

    def open(self, relpath):
        return self._archive.open(relpath)

    def files(self):
        for path in self._archive.namelist():
            yield path

    def list(self, *args, **kwargs):
        self._archive.printdir(*args, **kwargs)


class Archive(IArchive):
    """
    The API class that encapsulates an archive implementation.
    """
    EXTENSION_MAP = {
        '.docx': ZipArchive,
        '.egg': ZipArchive,
        '.jar': ZipArchive,
        '.odg': ZipArchive,
        '.odp': ZipArchive,
        '.ods': ZipArchive,
        '.odt': ZipArchive,
        '.pptx': ZipArchive,
        '.tar': TarArchive,
        '.tar.bz2': TarArchive,
        '.tar.gz': TarArchive,
        '.tgz': TarArchive,
        '.tz2': TarArchive,
        '.xlsx': ZipArchive,
        '.zip': ZipArchive,
    }

    def __init__(self, file, ext=''):
        """
        Arguments:
        * 'file' can be a string path to a file or a file-like object.
        * Optional 'ext' argument can be given to override the file-type
          guess that is normally performed using the file extension of the
          given 'file'.  Should start with a dot, e.g. '.tar.gz'.
        """
        cls = None
        filename = None
        if isinstance(file, six.string_types):
            filename = file
        else:
            try:
                filename = file.name
            except AttributeError:
                raise UnrecognizedArchiveFormat(
                    "File object not a recognized archive format.")
        lookup_filename = filename + ext
        base, tail_ext = os.path.splitext(lookup_filename.lower())
        cls = Archive.EXTENSION_MAP.get(tail_ext)
        if not cls:
            base, ext = os.path.splitext(base)
            cls = Archive.EXTENSION_MAP.get(ext)
        if not cls:
            raise UnrecognizedArchiveFormat(
                "Path not a recognized archive format: %s" % filename)
        self._archive = cls(file)

    def __repr__(self):
        return self._archive.__repr__()

    def __str__(self):
        return self._archive.__str__()

    def list(self):
        self._archive.list()

    def filename(self):
        return self._archive.filename()

    def files(self):
        return self._archive.files()

    def open(self, *args, **kwargs):
        return self._archive.open(*args, **kwargs)

    def read(self, *args, **kwargs):
        raise self._archive.read(*args, **kwargs)

    def extract(self, to_path='', method='safe'):
        if method == 'safe':
            self.check_files(to_path)
        elif method == 'insecure':
            pass
        else:
            raise ValueError("Invalid method option")
        self._archive.extract(to_path)

    def check_files(self, to_path=None):
        """
        Check that all of the files contained in the archive are within the
        target directory.
        """
        if to_path:
            target_path = os.path.normpath(os.path.realpath(to_path))
        else:
            target_path = os.getcwd()
        for filename in self.files():
            extract_path = os.path.join(target_path, filename)
            extract_path = os.path.normpath(os.path.realpath(extract_path))
            if not extract_path.startswith(target_path):
                raise UnsafeArchive(
                    "Archive member destination is outside the target"
                    " directory.  member: %s" % filename)
