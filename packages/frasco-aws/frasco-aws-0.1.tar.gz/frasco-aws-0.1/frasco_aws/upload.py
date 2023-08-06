from frasco_upload.backends import StorageBackend, file_upload_backend
from frasco import current_app


@file_upload_backend
class S3StorageBackend(StorageBackend):
    name = 's3'

    def save(self, file, filename):
        if current_app.features.aws.options['upload_async'] and current_app.features.exists('tasks'):
            tmpname = current_app.features.upload.save_uploaded_file_temporarly(file)
            current_app.features.tasks.enqueue('upload_file_to_s3',
                stream_or_filename=tmpname, filename=filename,
                mimetype=file.mimetype, delete_source=True)
        else:
            current_app.features.aws.upload_file_to_s3(file, filename)

    def url_for(self, filename, **kwargs):
        bucket = current_app.features.aws.options['upload_bucket']
        if current_app.features.aws.options['upload_signed_url']:
            b = current_app.features.aws.s3_connection.get_bucket(bucket)
            k = b.get_key(filename)
            kwargs.setdefault('expires_in',
                current_app.features.aws.options['upload_s3_urls_ttl'])
            return k.generate_url(**kwargs)
        return 'https://%s.s3.amazonaws.com/%s' % (bucket, filename)