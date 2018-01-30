# ArchivesSnake
A client library for working with the ArchivesSpace API

## Purpose
As institutions have adopted ArchivesSpace, a variety of practitioners and institutions have written scripts making use of
the backend API to accomplish various bulk tasks not supported (yet) by the interface.  ArchivesSnake is intended to be
a comprehensive client library, to reduce duplication of effort and simplify scripting ArchivesSpace.

## Prior Art
Here are listed several examples of pre-ASnake scripts that operate on ArchivesSpace - please feel free to submit your
own via pull request!

* [RAC Examples](RAC_links.md)
* [Duke Examples](Duke_links.md)
* [Outline of UAlbany Draft Library](ualbanyExample.md)
* [Harvard/Smith Ingest Client/Scripts](HarvardSmithLinks.md)

## Requirements
ArchivesSnake has the following requirements.

- Python 3.4 or higher
- ability to install packages via pip ([Pipenv](https://docs.pipenv.org/) is recommended for development)

## Installation
Very soon, ArchivesSnake should be registered with pypi, but currently, to install, follow these steps.

``` bash
git clone https://github.com/archivesspace-labs/ArchivesSnake.git
cd ArchivesSnake
python3 setup.py sdist
pip install dist/ArchivesSnake-0.1.tar.gz
```

You'll need an internet connection to fetch ASnake's dependencies.

## Usage
To start, here's a simple, fairly complete example - fetching the JSON representation of all the repositories from an ArchivesSpace instance and saving it to a variable.

``` python
from asnake import ASnakeClient

client = ASnakeClient(baseurl="http://my.aspace.backend.url.edu:4567",
                      username="admin",
                      password="admin")
client.authorize()
repos = client.get("repositories").json()

# do what thou wilt with some repos
```

Right now, there's a single user-visible class that's useful, ASnakeClient, which is a convenience wrapper
over the [requests](http://docs.python-requests.org/en/master/) module that handles configuration, authentication to
ArchivesSpace, and prepends a baseurl to API paths.

So this:

``` python
requests.get("http://my.aspace.backend.url.edu:4567/repositories")
```

is equivalent to:

``` python
client.get('repositories')
```

In addition to saving typing, the result of this is that the url fragments used as identifiers in ArchivesSpace `ref` objects can often (always?) be passed directly to these methods.

## Configuration

As you can see in the example above, you can configure the client with a baseurl, username, and password in code when creating the client object.
You can also define a file in the [YAML](http://yaml.org/) configuration language; by default, ASnake looks for a file called `.archivessnake.yml` in the home directory of the user running it.  If an environment variable `ASNAKE_CONFIG_FILE` is set, ASnake will treat it as a filename and search for a YAML config file there.

An example config:

``` yaml
baseurl: http://localhost:4567
username: admin
password: admin
```

Default values corresponding to the admin account of an unaltered local development instance of ASpace are included as fallback values.
