from setuptools import setup, find_packages

setup(
    name="ArchivesSnake",
    version="0.1",
    packages=find_packages(),
    zip_safe=False,
    install_requires=["requests"]
)
