"""
A custom Storage interface for storing files to S3 via OpenS3
"""
import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from openS3 import OpenS3
from openS3.constants import AWS_DATETIME_FORMAT
from openS3.utils import S3IOError
from django_openS3.constants import S3_STATIC_DIR, S3_MEDIA_DIR


class S3Storage(Storage):
    """
    A custom storage implementation for use with py3s3.
    An instance of this class can be used to move a py3s3 file
    up to or down from AWS.
    """
    def __init__(self, name_prefix, bucket, aws_access_key, aws_secret_key):
        self.name_prefix = None
        if name_prefix:
            if len(name_prefix) < 3:
                raise ImproperlyConfigured('Given name prefix is too short. '
                                           'Given name prefix {}'.format(name_prefix))
            if name_prefix[0] != '/' or name_prefix[-1] != '/':
                raise ImproperlyConfigured('Given name prefix must start and end with a slash. '
                                           'Given name prefix {}'.format(name_prefix))
            self.name_prefix = name_prefix
        self.opener = OpenS3(bucket, aws_access_key, aws_secret_key)

    def _open(self, name, mode='rb'):
        """
        Retrieves the specified file from storage.
        """
        name = self._prepend_name_prefix(name)
        with self.opener(name, mode) as fd:
            content = fd.read()
        return ContentFile(content, name)

    def _save(self, name, content):
        name = self.get_valid_name(name)
        name = self._prepend_name_prefix(name)

        with self.opener(name, 'wb') as fd:
            fd.write(content.read().decode())
        return name

    def get_valid_name(self, name):
        # TODO Implement this method in a AWS friendly way.
        # Don't use Django's get_valid_name as it strips slashes from the name.
        return name

    def _prepend_name_prefix(self, name):
        """Return file name (ie. path) with the prefix directory prepended"""
        if not self.name_prefix:
            return name
        base = self.name_prefix
        if name[0] == '/':
            name = name[1:]
        return base + name

    def delete(self, name):
        """
        Deletes the specified file from the storage system.
        """
        name = self._prepend_name_prefix(name)
        with self.opener(name) as fd:
            fd.delete()

    def exists(self, name):
        """
        Returns True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        name = self._prepend_name_prefix(name)
        with self.opener(name) as fd:
            return fd.exists()

    def listdir(self, path):
        """
        Lists the contents of the specified path, returning a 2-tuple of lists;
        the first item being directories, the second item being files.
        """
        with self.opener(path) as fd:
            return fd.listdir()

    def size(self, name):
        """
        Returns the total size, in bytes, of the file specified by name.
        """
        name = self._prepend_name_prefix(name)
        with self.opener(name) as fd:
            return fd.size

    def url(self, name):
        """
        Returns an absolute URL where the file's contents can be accessed
        directly by a Web browser.
        """
        name = self._prepend_name_prefix(name)
        return self.opener(name).url

    def modified_time(self, name):
        """
        Returns the last modified time (as datetime object) of the file
        specified by name.
        """
        name = self._prepend_name_prefix(name)
        with self.opener(name) as fd:
            fd.exists()  # Call .exists() to populate .response_headers
            response_headers = fd.response_headers

        if 'Last-Modified' not in response_headers:
            raise S3IOError('"Last-Modified" header not found for S3 object {}'.format(name))
        datetime_str = response_headers['Last-Modified']
        return datetime.datetime.strptime(datetime_str, AWS_DATETIME_FORMAT)


class S3StaticStorage(S3Storage):
    def __init__(self,
                 name_prefix=getattr(settings, 'S3_STATIC_DIR', None) or S3_STATIC_DIR,
                 bucket=settings.AWS_STORAGE_BUCKET_NAME,
                 aws_access_key=settings.AWS_ACCESS_KEY_ID,
                 aws_secret_key=settings.AWS_SECRET_ACCESS_KEY):
        super().__init__(name_prefix, bucket, aws_access_key, aws_secret_key)


class S3MediaStorage(S3Storage):
    def __init__(self,
                 name_prefix=getattr(settings, 'S3_MEDIA_DIR', None) or S3_MEDIA_DIR,
                 bucket=settings.AWS_STORAGE_BUCKET_NAME,
                 aws_access_key=settings.AWS_ACCESS_KEY_ID,
                 aws_secret_key=settings.AWS_SECRET_ACCESS_KEY):
        super().__init__(name_prefix, bucket, aws_access_key, aws_secret_key)