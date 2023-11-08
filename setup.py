from setuptools import setup, find_packages
from pathlib import Path

def get_install_requires() -> list[str]:
    fname = Path(__file__).parent / "src" / "requirements.txt"
    targets = []
    if fname.exists():
        with open(fname, 'r') as f:
            targets = f.read().splitlines()
    return targets

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
    install_requires=get_install_requires(),
)
