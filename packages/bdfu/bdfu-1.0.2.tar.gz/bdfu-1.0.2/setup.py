from setuptools import setup, find_packages

def read_file(filename):
    """Read a file or return the empty string if there is some error."""
    try:
        return open(filename, 'r').read()
    except IOError:
        return ''

setup(
    name="bdfu",
    version="1.0.2",
    packages=find_packages(),
    long_description=read_file("README.md"),
    short_description='A "brain dead"-simple file upload server',
    entry_points=dict(
        console_scripts=[
            'bdfu = bdfu.tool:main',
        ],
    ),
    install_requires=[
        # Py2/3 compat
        "future",

        # Authentication
        "pyjwt",

        # Client
        "requests",

        # Server
        "flask",
        "flask-jwt",

        # Command-line tool
        "docopt",
    ],
    tests_require=[
        "pytest",
        "mock",
        "responses",
    ],
)
