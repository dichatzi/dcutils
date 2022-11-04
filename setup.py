from setuptools import setup, find_packages
import codecs
import os

VERSION = "0.0.1"
DESCRIPTION = "Utilities developed by Dr. Dimitris I. Chatzigiannis"
LONG_DESCRIPTION = "Various utilitites related to database connection, printing files, etc that are continuously used"

setup(
    name="dcutils",
    version=VERSION,
    author="Dr. Dimitris I. Chatzigiannis",
    author_email="dimitris.chatzigiannis@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,    
    packages=find_packages(),
    install_requires=["psycopg2", "pandas", "sqlalchemy"],
    keywords=["utilities", "database_connection"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)
