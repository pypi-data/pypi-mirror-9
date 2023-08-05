import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="boto-s3-shim",
    version="0.0.2",
    author="Graham Christensen",
    author_email="graham@grahamc.com",
    description="Inject an alternative S3 server into any boto-based project",
    long_description=read('README.rst'),
    license="MIT",
    keywords="boto s3 fakes3",
    url="http://github.com/grahamc/boto_s3_shim",
    packages=["boto_s3_shim"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
