# -*- coding: utf-8 -*-
class Filesystem(object):

    """The abstracted api that the user will interface with when dealing
    with different types of filesystems.

    Example:

    .. code-block:: python

        from watson import filesystem

        fs = filesystem.Filesystem(filesystem.backends.Local())
        content = fs.read('/path/to/file')
        print(content)
    """

    backend = None

    def __init__(self, backend):
        self.backend = backend

    def read(self, file, options=None):
        """Reads a file (and then closes it).

        Args:
            file (string): The file to read
            options (dict): A dict of args that will be passed to open()
        """
        return self.backend.read(file, options=options)

    def exists(self, path):
        """Verifies if a path exists.

        Args:
            path (string): The path to verify

        Returns:
            Boolean based on whether or not it exists.
        """
        return self.backend.exists(path)

    def write(self, file, content, options=None):
        """Writes some specific content to a file.

        Performing this call will overwrite any content that exists within
        the file.
        If the file does not exist (or the path), it will be created.

        Args:
            file (string): The file to write to
            content (mixed): The content to write to the file.
            options (dict): A dict of args that will be passed to open()
        """
        return self.backend.write(file, content, options=options)

    def append(self, file, content, options=None):
        """Appends specific content to a file.

        Similar function to write(), except that any content will be appended
        to the end of the file.

        Args:
            file (string): The file to write to
            content (mixed): The content to write to the file.
            options (dict): A dict of args that will be passed to open()
        """
        return self.backend.append(file, content, options=options)

    def delete(self, path):
        """Deletes a path from the filesystem.

        If a directory is specified, its contents will also be removed.

        Args:
            path (string): The path to delete
        """
        return self.backend.delete(path)

    def move(self, path, new_path):
        """Moves a file/directory to a new location.

        Args:
            path (string): The path to move to
            new_path (string): The new location for the file/directory
        """
        return self.backend.move(path, new_path)

    def copy(self, path, new_path):
        """Copies a file/directory to a new location.

        Args:
            path (string): The path to copy to
            new_path (string): The new location for the file/directory
        """
        return self.backend.copy(path, new_path)

    def create(self, path, is_dir=False):
        """Creates a new file/directory.

        If any parent directories in the path do not exist they will be
        created.

        Args:
            path (string): The path to create
            is_dir (boolean): Whether or not to create the path as a directory
        """
        return self.backend.create(path, is_dir)

    # convenience methods
    def __contains__(self, file):
        """Convenience method for exists()

        Example:

        .. code-block:: python
            fs = Filesystem()
            if '/path/to/file' in fs:
                return True
        """
        return self.exists(file)

    def __getitem__(self, file):
        """Convenience method for read()

        Example:

        .. code-block:: python
            fs = Filesystem()
            content = fs['/path/to/file']
        """
        return self.read(file)

    def __setitem__(self, file, content):
        """Convenience method for write()

        Example:

        .. code-block:: python
            fs = Filesystem()
            fs['/path/to/file'] = 'testing'
        """
        return self.write(file, content)
