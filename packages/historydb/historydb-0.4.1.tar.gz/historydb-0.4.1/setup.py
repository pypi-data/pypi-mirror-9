try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="historydb",
    packages=["historydb"],
    version="0.4.1",
    description="HistoryDB implemented in Python",
    author="ASD Technologies",
    author_email="admin@asdco.ru",
    url="https://bitbucket.org/asdtech/historydb-python",
    install_requires=[],
    license="BSD License",
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    long_description=open("README.rst").read()
)
