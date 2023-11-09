from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="GOB-Export",
    version="0.1",
    url="https://github.com/Amsterdam/GOB-Export.git",
    license="MPL2",
    author="Amsterdam",
    author_email="datapunt@amsterdam.nl",
    description="GOB-Export",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "Flask==2.3.2",
        "Flask-Cors==3.0.10",
        "pysftp==0.2.9",
        "freezegun==1.2.2",
        "requests-mock~=1.11.0",
        "gobconfig @ git+https://github.com/Amsterdam/GOB-Config.git@v0.14.2",
        "gobcore @ git+https://github.com/Amsterdam/GOB-Core.git@v2.23.0"
    ]
)
