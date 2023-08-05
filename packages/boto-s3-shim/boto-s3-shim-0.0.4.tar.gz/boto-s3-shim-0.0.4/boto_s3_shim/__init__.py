import os
from urllib.parse import urlparse
from boto.s3.connection import S3Connection
from boto.s3.connection import OrdinaryCallingFormat


override = os.environ.get('S3_OVERRIDE', False)
if override:
    override_to = urlparse(str(override))

    old_init = S3Connection.__init__
    def new__init__(self, *k, **kwargs):
        kwargs['host'] = override_to.hostname
        kwargs['port'] = int(override_to.port)
        kwargs['calling_format'] = OrdinaryCallingFormat()
        kwargs['is_secure'] = override_to.scheme == 'secure'
        old_init(self, *k, **kwargs)

    S3Connection.__init__ = new__init__

