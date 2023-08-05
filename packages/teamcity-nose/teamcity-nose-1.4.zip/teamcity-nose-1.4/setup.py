from setuptools import setup
setup(
    name = "teamcity-nose",
    version = "1.4",
    author = 'Leonid Shalupov',
    author_email = 'Leonid.Shalupov@jetbrains.com',
    description = '[Obsolete] use teamcity-messages package',
    long_description = """Plugin is OBSOLETE, use teamcity-messages package instead.

See https://pypi.python.org/pypi/teamcity-messages
""",
    license = 'Apache 2.0',
    keywords = '',
    classifiers = [
        'Development Status :: 7 - Inactive',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
    url = "http://pypi.python.org/pypi/teamcity-nose",
    platforms = ["any"],

    install_requires = [
        "teamcity-messages >=1.12"
    ],
)
