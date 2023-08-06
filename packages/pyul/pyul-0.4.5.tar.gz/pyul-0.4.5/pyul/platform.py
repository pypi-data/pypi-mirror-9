from __future__ import absolute_import
import os
import sys
import six
from enum import Enum
import platform as _platform
from .coreUtils import Singleton

__all__ = ['Platforms', 'platform']


class Platforms(Enum):
    unknown = 1
    windows = 2
    macosx = 3
    linux = 4
    android = 5
    ios = 6


@six.add_metaclass(Singleton)
class Platform(object):
    _platform_android = None
    _platform_ios = None

    def __eq__(self, other):
        return other == self._get_platform()

    def __ne__(self, other):
        return other != self._get_platform()

    def __str__(self):
        return self._get_platform().name

    def __repr__(self):
        return '<platform name: \'{platform}\' from: \n{instance}>'.format(
            platform=self._get_platform(),
            instance=super(Platform, self).__repr__()
        )

    def __hash__(self):
        return self._get_platform().__hash__()

    def _get_platform(self):
        if self._platform_android is None:
            # ANDROID_ARGUMENT and ANDROID_PRIVATE are 2 environment variables
            # from python-for-android project
            self._platform_android = 'ANDROID_ARGUMENT' in os.environ
        if self._platform_ios is None:
            self._platform_ios = 'IOS_ARGUMENT' in os.environ
        # On android, sys.platform return 'linux2', so prefer to check the
        # import of Android module than trying to rely on sys.platform.
        if self._platform_android is True:
            return Platforms.android
        if self._platform_ios is True:
            return Platforms.ios
        if sys.platform in ('win32', 'cygwin'):
            return Platforms.windows
        if sys.platform == 'darwin':
            return Platforms.macosx
        if sys.platform[:5] == 'linux':
            return Platforms.linux
        return Platforms.unknown

    @property
    def name(self):
        platform = self._get_platform()
        if platform == Platforms.linux:
            return '-'.join(_platform.linux_distribution()[:2])
        if platform == Platforms.macosx:
            return '-'.join(['MacOS', _platform.mac_ver()[0], _platform.mac_ver()[-1]])
        if platform == Platforms.windows:
            return '-'.join(['Windows', _platform.win32_ver()[0]])
        return Platforms.unknown.name

    def is_64bit():
        """Checks, if the platform is a 64-bit machine."""
        is64bit = sys.maxsize > 2 ** 32
        if sys.platform == "cli":
            is64bit = sys.executable.endswith("ipy64.exe")
        return is64bit


platform = Platform()
