# -*- coding: utf-8 -*-
from boto3 import session
from watson.filesystem import exceptions
from watson.filesystem.backends import abc


class Backend(abc.Backend):

    """Provides a backend for dealing with the Amazon S3.

    Internally makes use of Boto3, and assumes that the relevant bucket
    has already been created within S3.

    Example:

        .. code-block:: python
            from watson.filesystem import backends, Filesystem

            aws_config = {
                'aws_access_key'
            }
            fs = Filesystem(backends.S3(
                'aws_access_key': 'XXXXX',
                'aws_secret_access_key': 'XXXXXX',
                'bucket': 'BUCKET_NAME'
            ))
            fs.write('document.txt', 'The content of the document')
    """

    session = None
    client = None
    resource = None
    bucket = None

    def __init__(self, **kwargs):
        """Initializes the S3 backend for watson.filesystem.

        Kwargs:
            aws_access_key (string): The AWS Access Key
            aws_secret_access_key (string): The AWS Secret Access Key
            bucket (string): The bucket name to work out of
        """
        self.session = session.Session(
            aws_access_key_id=kwargs['aws_access_key'],
            aws_secret_access_key=kwargs['aws_secret_access_key'])
        self.client = self.session.client('s3')
        self.resource = self.session.resource('s3')
        self.bucket = kwargs['bucket']

    def read(self, file, options=None):
        obj = self._object(file)
        try:
            response = obj.get()
        except Exception as e:
            raise exceptions.NotFoundError from e
        _options = {
            'encoding': 'utf-8'
        }
        if options:
            _options.update(options)
        body = response['Body'].read()
        return body.decode(_options['encoding'])

    def exists(self, path):
        obj = self._object_summary(path)
        summary = None
        try:
            summary = obj.get()
            return summary['ContentLength'] >= 0
        except:
            return False

    def write(self, file, content, options=None):
        obj = self._object(file)
        args = {
            'ACL': 'public-read'  # public-read | private
        }
        if options:
            args.update(options)
        args['Body'] = content
        obj.put(**args)
        return True

    def append(self, file, content, options=None):
        existing_content = self.read(file)
        existing_content += content
        return self.write(file, existing_content, options)

    def delete(self, path):
        obj = self._object(path)
        try:
            obj.delete()
        except:
            return False
        return True

    def move(self, path, new_path):
        self.copy(path, new_path)
        self.delete(path)
        return True

    def copy(self, path, new_path):
        self.client.copy_object(
            Bucket=self.bucket,
            CopySource='{}/{}'.format(self.bucket, path),
            Key=new_path)
        return True

    def create(self, path, is_dir=True, parents=True):
        if is_dir:
            path += '/'
        obj = self._object(path)
        obj.put()
        return True

    # internals

    def _object(self, path):
        return self.resource.Object(bucket_name=self.bucket, key=path)

    def _object_summary(self, path):
        return self.resource.ObjectSummary(
            bucket_name=self.bucket, key=path)
