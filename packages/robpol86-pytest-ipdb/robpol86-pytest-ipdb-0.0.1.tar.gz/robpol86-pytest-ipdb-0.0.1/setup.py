from setuptools import setup

setup(
    name="robpol86-pytest-ipdb",
    packages=["pytestipdb"],
    version="0.0.1",
    description="pytest-ipdb installable from pip. Using this until https://github.com/mverteuil/pytest-ipdb/issues/9 is resolved.",
    author="Robpol86",
    author_email="robpol86@gmail.com",
    url="https://github.com/mverteuil/pytest-ipdb",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Communications :: Email",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Testing",
    ],
    install_requires=[
        'pytest>=2.6.3',
        'ipdb',
    ],
    # the following makes a plugin available to py.test
    entry_points = {
        "pytest11": [
            "pytestipdb = pytestipdb.ptipdb",
        ]
    },
)
