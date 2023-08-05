import os
import boto
from urllib.parse import urlparse
from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat


override = os.environ.get('S3_OVERRIDE', False)
if override:
    override_to = urlparse(str(override))

    def conn_s3(aws_access_key_id=None, aws_secret_access_key=None, **kwargs):
        kwargs['host'] = override_to.hostname
        kwargs['port'] = int(override_to.port)
        kwargs['calling_format'] = OrdinaryCallingFormat()
        kwargs['is_secure'] = override_to.scheme == 'secure'

        return S3Connection(aws_access_key_id, aws_secret_access_key, **kwargs)

    boto.connect_s3 = conn_s3
