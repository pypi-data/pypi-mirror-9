circle-asset |Latest Version|
=============================

|Circle CI|

A tool for getting the latest assets from CircleCI.

::

    usage: circle-asset [-h] [--version] [--api-root API_ROOT] [--token [TOKEN]]
                        [--branch BRANCH] [--accept-failed] [--build BUILD]
                        username project [artifact [artifact ...]]

    Get the latest assets from CircleCI

    positional arguments:
      username             GitHub username
      project              GitHub project
      artifact             Artifact name (or pattern) to get

    optional arguments:
      -h, --help           show this help message and exit
      --version            show program's version number and exit
      --api-root API_ROOT  API root for CircleCI
      --token [TOKEN]      API key
      --branch BRANCH      Project branch
      --accept-failed      Accepts artifacts from the latest build
      --build BUILD        Go to a specific build

.. |Latest Version| image:: https://pypip.in/version/circle_asset/badge.svg
   :target: https://pypi.python.org/pypi/circle-asset/
.. |Circle CI| image:: https://circleci.com/gh/prophile/circle-asset.svg?style=svg
   :target: https://circleci.com/gh/prophile/circle-asset
