# pyi - PYthon Information

A simple cli that scrapes pypi json endpoints for package data.

It can be used to easily get basic stats on a package without the need to go to pypi to look it up.



## Installation

Latest stable release from pypi.

Note: currently only python 2.7 is supported!

```
$ pip install pyi
```

or from source

```
$ python setup.py install
```


## Runtime dependencies

 - docopt 0.6.2
 - PyYaml 3.11


## Usage

```
$ pyi basic requests

$ pyi description requests

$ pyi downloads requests

$ pyi releases requests

$ pyi release 2.5.0 requests

$ pyi raw requests
```


# Licensing

MIT, See License.txt for details

Copyright (c) 2015 Johan Andersson
