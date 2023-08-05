Usage
-----

Set the S3_OVERRIDE environment variable, import boto_s3_shim, and get on with
it.

Example possible values:

insecure://your-fake-s3-server:80
insecure://your-fake-s3-server:80
secure://your-fake-s3-server:443
secure://your-fake-s3-server:4430

This exists to work around https://github.com/boto/boto/pull/2929 and
https://github.com/boto/boto/issues/2617. Please don't use it in production.

