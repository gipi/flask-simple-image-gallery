"""
This module aims to create a model having the filesystem as backend, since
if someone don't want to add extra metadata more than the metadata given
by the file informations is useless to use a database.

TODO: traverse directory.
"""
import settings
import os

try:
    settings.GALLERY_ROOT_DIR
except:
    raise AttributeError('You forget to define GALLERY_ROOT_DIR setting variable')


class FilesystemObjectDoesNotExist(Exception):
    pass

class FilesystemObject(object):
    def __init__(self, filename):
        """Create an object from the information of the given filename"""
        self.root_dir = settings.GALLERY_ROOT_DIR
        self.filename  = filename
        self.abspath  = os.path.join(self.root_dir, filename)

        try:
            stats = os.stat(self.abspath)
        except IOError as e:
            raise FilesystemObjectDoesNotExist(e.message)

        self.timestamp = stats.st_mtime

    @classmethod
    def all(cls):
        """Return a list of files contained in the directory pointed by settings.GALLERY_ROOT_DIR.
        """
        return [cls(x) for x in os.listdir(settings.GALLERY_ROOT_DIR)]

class Image(FilesystemObject):
    pass
