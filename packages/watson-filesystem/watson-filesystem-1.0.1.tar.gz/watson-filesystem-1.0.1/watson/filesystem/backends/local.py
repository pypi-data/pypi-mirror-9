# -*- coding: utf-8 -*-
from contextlib import suppress
import pathlib
import shutil
from watson.filesystem import exceptions
from watson.filesystem.backends import abc


class Backend(abc.Backend):

    """Provides a backend for dealing with the local filesystem.

    Internally makes use of pathlib and shutil. See
    watson.filesystem.Filesystem for API documentation.
    """

    def read(self, file, options=None):
        file = self._resolve_path(file)
        _options = {
            'mode': 'r',
            'encoding': 'utf-8'
        }
        if options:
            _options.update(options)
        try:
            with file.open(**_options) as f:
                return ''.join(f.readlines())
        except Exception as e:
            raise exceptions.NotFoundError from e

    def exists(self, path):
        try:
            path = self._resolve_path(path)
            return path.exists()
        except FileNotFoundError:
            return False

    def write(self, file, content, options=None):
        try:
            file = self._resolve_path(file)
        except:
            file = pathlib.Path(file)
            self.create(file.parent)
        _options = {
            'mode': 'w',
            'encoding': 'utf-8'
        }
        if options:
            _options.update(options)
        with file.open(**_options) as f:
            f.write(content)
        return True

    def append(self, file, content, options=None):
        return self.write(
            file,
            content,
            {
                'mode': 'a'
            }
        )

    def delete(self, path):
        try:
            path = self._resolve_path(path)
        except:
            return False
        if path.is_dir():
            try:
                path.rmdir()
            except OSError:
                shutil.rmtree(str(path))
        else:
            path.unlink()
            return True

    def move(self, path, new_path):
        path = self._resolve_path(path)
        path.rename(new_path)
        return new_path

    def copy(self, path, new_path):
        path = self._resolve_path(path)
        if path.is_dir():
            shutil.copytree(str(path), new_path)
        else:
            shutil.copy2(str(path), new_path)
        return new_path

    def create(self, path, is_dir=True, parents=True):
        path = pathlib.Path(path)
        if is_dir:
            with suppress(Exception):
                path.mkdir(parents=parents)
        else:
            parent_dir = path.parent
            with suppress(Exception):
                parent_dir.mkdir(parents=parents)
            path.touch()
        return str(path)

    # internals

    def _resolve_path(self, path):
        # Converts a path into a Path object.
        if isinstance(path, pathlib.Path):
            return path.resolve()
        return pathlib.Path(path).resolve()
