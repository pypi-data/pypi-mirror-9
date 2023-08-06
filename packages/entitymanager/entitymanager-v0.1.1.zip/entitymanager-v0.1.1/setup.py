import os
from distutils.core import setup

version = 'v0.1.1'

setup(
    name="entitymanager",
    packages=['pyentity'],
    version=version,
    keywords=["mongo", "mongodb", "pyentity", "motor", "tornado"],
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md"), "r").read(),
    description="An s   imple object-document mapping for mongodb-motor and tornado applications.",
    author="Leonardo Souza",
    author_email="leo.desouza@gmail.com",
    url="https://github.com/leodesouza/pyentity",
    download_url="https://github.com/leodesouza/pyentity/tree/v0.1.0-beta",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
    ],
    license='http://www.apache.org/licenses/LICENSE-2.0',
)
