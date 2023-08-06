from setuptools import find_packages, setup

setup(
    name="crc-nd.utils",    # Note the use of hyphen; setuptools would convert an underscore to hyphen automatically,
                            # which is confusing.  See http://stackoverflow.com/q/19097057/1258514
    version="0.2.0",

     # Metadata for PyPI
    description="Utility code for Python projects",
    author='Center for Research Computing, University of Notre Dame',
    author_email="crc-ci-developers@listserv.nd.edu",
    url="https://github.com/crc-nd/py-utils",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # This keyword argument is a workaround to ensure the classifiers appear on PyPI if the package is created with
    # Python 2.7.2 or earlier (see http://stackoverflow.com/q/26284609/1258514 for details).
    provides=['crc_nd.utils'],

    packages=find_packages(),
    namespace_packages=['crc_nd', ],
    install_requires=['path.py==5.3'],
)
