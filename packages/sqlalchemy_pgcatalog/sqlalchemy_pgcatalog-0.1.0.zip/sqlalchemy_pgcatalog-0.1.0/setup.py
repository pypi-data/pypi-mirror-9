"""
Setup for sqlalchemy_pgcatalog
"""

from setuptools import find_packages, setup

setup_params = dict(
    name="sqlalchemy_pgcatalog",
    description="SQLAlchemy definitions for PostgreSQL catalog tables",
    packages=find_packages(),
    version="0.1.0",
    install_requires=["sqlalchemy>=0.7.0"],
    author="Renshaw Bay",
    author_email="technology@renshawbay.com",
    url="https://github.com/renshawbay/sqlalchemy_pgcatalog",
    classifiers=["Topic :: Database",
                 "License :: OSI Approved :: MIT License",
                 "Programming Language :: Python :: 3.2",
                 "Programming Language :: Python :: 3.3",
                 "Programming Language :: Python :: 3.4"]
)

if __name__ == '__main__':
    setup(**setup_params)
