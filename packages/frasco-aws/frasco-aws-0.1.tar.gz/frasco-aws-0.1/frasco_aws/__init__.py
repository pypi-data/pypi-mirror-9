from frasco import Feature, action, cached_property
import boto
import os
from tempfile import NamedTemporaryFile


class AwsFeature(Feature):
    name = 'aws'
    ignore_attributes = ['s3_connection']
    defaults = {'upload_bucket': None,
                'upload_filename_prefix': '',
                'upload_acl': 'public-read',
                'upload_async': False,
                'upload_signed_url': False,
                'upload_s3_urls_ttl': 3600}

    @cached_property
    def s3_connection(self):
        return boto.connect_s3(self.options.get('access_key'), self.options.get('secret_key'))

    @action()
    def upload_file_to_s3(self, stream_or_filename, filename, bucket=None, prefix=None,\
                          acl=None, mimetype=None, delete_source=False):
        b = self.s3_connection.get_bucket(bucket or self.options['upload_bucket'])
        prefix = prefix or self.options.get('upload_filename_prefix', '')
        k = b.new_key(prefix + filename)
        acl = acl or self.options['upload_acl']
        headers = None
        if mimetype:
            headers = {'Content-Type': mimetype}
        is_filename = isinstance(stream_or_filename, (str, unicode))
        if is_filename:
            k.set_contents_from_filename(stream_or_filename, headers, policy=acl)
        else:
            k.set_contents_from_string(stream_or_filename.readlines(), headers, policy=acl)
        if is_filename and delete_source:
            os.remove(stream_or_filename)

    @action(default_option='filename')
    def delete_s3_file(self, filename, bucket=None, prefix=None):
        b = self.s3_connection.get_bucket(bucket or self.options['upload_bucket'])
        prefix = prefix or self.options.get('upload_filename_prefix', '')
        b.delete_key(prefix + filename)


try:
    import upload
except ImportError:
    pass