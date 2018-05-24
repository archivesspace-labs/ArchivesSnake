from setuptools import setup, find_packages

setup(
    name="ArchivesSnake",
    url="https://github.com/archivesspace-labs/ArchivesSnake",
    description="ArchivesSpace Client Library",
    long_description="""A client library for the ArchivesSpace REST API.""",
    author="ArchivesSnake Developer Group",
    author_email="asnake.developers@gmail.com",
    version="0.4.1",
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
    ],
    python_requires="~=3.4",
    install_requires=[
        "attrs",
        "boltons",
        "pyyaml",
        "requests",
	"structlog",
	"more_itertools",
    ],
)
