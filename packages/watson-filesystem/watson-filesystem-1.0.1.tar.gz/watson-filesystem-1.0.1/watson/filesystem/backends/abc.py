# -*- coding: utf-8 -*-
import abc
from watson.filesystem import Filesystem


class Backend(metaclass=abc.ABCMeta):

    """The abstract base class for filesystem backends.
    """

    def __init__(self, **kwargs):
        pass

    @classmethod
    def factory(cls, **kwargs):
        """Provides a convenient method of initializing the filesystem
        directly off the backend.
        """
        return Filesystem(cls(**kwargs))

    @abc.abstractmethod
    def read(self, file, options=None):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def exists(self, path):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def write(self, file, content, options=None):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def append(self, file, content, options=None):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def delete(self, path):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def move(self, path, new_path):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def copy(self, path, new_path):
        raise NotImplementedError  # pragma: no cover

    @abc.abstractmethod
    def create(self, path, is_dir=False):
        raise NotImplementedError  # pragma: no cover
