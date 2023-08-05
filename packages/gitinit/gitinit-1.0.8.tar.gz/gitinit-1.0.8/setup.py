import os
from setuptools import setup, find_packages

__currdir__ = os.getcwd()
__readme__ = os.path.join(__currdir__, 'README')

setup(
    name="gitinit",
    version="1.0.8",
    author="Bibhas C Debnath",
    author_email="me@bibhas.in",
    description=("Initiates git with gitignore for provided language"),
    license="GPL",
    keywords="cli git",
    url="https://github.com/iambibhas/gitinit",
    packages=find_packages(),
    long_description=open(__readme__).read(),
    package_data={'gitinit': ['*.gitignore', 'gitinit/gitignores/*.gitignore', 'gitinit/gitignores/Global/*.gitignore']},
    include_package_data=True,
    entry_points={"console_scripts": ["gitinit=gitinit.gitinit:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Programming Language :: Python"
    ]
)
