"""
This module aims to create a model having the filesystem as backend, since
if someone don't want to add extra metadata more than the metadata given
by the file informations is useless to use a database.

TODO
    - traverse directory
    - check symlink
"""
from flask import current_app
from werkzeug import secure_filename
from pathlib import Path
import os


class FilesystemObjectDoesNotExist(Exception):
    pass


class FilesystemObject(object):

    def __init__(self, filename, post=None, root=None):
        """Create an object from the information of the given filename or from a
        uploaded file.

        Example of usage:

            if request.method == 'POST' and 'photo' in request.POST:
                f = FilesystemObject('cats.png', request.POST['photo'])

        """
        self.root_dir = Path(root)
        self.path = Path(filename if not post else secure_filename(post.filename))
        self.abspath = self.root_dir / self.path

        if post:
            self.upload(post)

        try:
            stats = os.stat(self.abspath)
            self.timestamp = stats.st_mtime
        except IOError as e:
            current_app.logger.error(e)
            current_app.logger.error(f'{self!r}')
            raise FilesystemObjectDoesNotExist(e)

    def __repr__(self):
        return f'<{self.__class__.__name__}(filename={self.path}, root={self.root_dir})>'

    def upload(self, post):
        """Get a POST file and save it to the settings.GALLERY_ROOT_DIR"""
        # TODO: handle filename conflicts
        # http://flask.pocoo.org/docs/patterns/fileuploads/
        current_app.logger.info(f'saving at \'{self.abspath}\'')
        post.save(str(self.abspath))

    @classmethod
    def all(cls, root):
        """Return a list of files contained in the directory pointed by settings.GALLERY_ROOT_DIR.
        """
        return [cls(filename=x, root=root) for x in os.listdir(root)]


class Image(FilesystemObject):
    pass
