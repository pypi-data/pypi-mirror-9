[![Build Status](https://travis-ci.org/urschrei/pyzotero.png?branch=dev)](https://travis-ci.org/urschrei/pyzotero) [![Wheel Status](https://pypip.in/wheel/Pyzotero/badge.svg)](https://pypi.python.org/pypi/Pyzotero/) [![Supported Python versions](https://pypip.in/py_versions/Pyzotero/badge.svg)](https://pypi.python.org/pypi/Pyzotero/)

# Quickstart #

1. `pip install pyzotero`
2. You'll need the ID of the personal or group library you want to access:
    - Your **personal library ID** is available [here](https://www.zotero.org/settings/keys), in the section `Your userID for use in API calls`.
    - For **group libraries**, the ID can be found by opening the group's page: `https://www.zotero.org/groups/groupname`, and hovering over the `group settings` link. The ID is the integer after `/groups/`.
3. You'll also need<sup>†</sup> to get an **API key** [here][2].
4. Are you accessing your own Zotero library? `library_type` is `user`.
5. Are you accessing a shared group library? `library_type` is `group`.  

Then:

``` python
from pyzotero import zotero
zot = zotero.Zotero(library_id, library_type, api_key)
items = zot.top(limit=5)
# we've retrieved the latest five top-level items in our library
# we can print each item's item type and ID
for item in items:
    print('Item: %s | Key: %s') % (item['data']['itemType'], item['data']['key'])
```

# Documentation #
Full documentation of available Pyzotero methods, code examples, and sample output is available on [Read The Docs][3].

# Installation #
* Using [pip][10]: `pip install pyzotero` (it's available as a wheel, and is tested on Python 2.7 and 3.4)
* From a local clone, if you wish to install Pyzotero from a specific branch: 

Example:

``` bash
git clone git://github.com/urschrei/pyzotero.git
cd pyzotero
git checkout dev
pip install .
```

## Testing ##

Run `test_zotero.py` in the [pyzotero/test](test) directory, or, using [Nose][7], `nosetests` from the top-level directory.

## Issues ##

Pyzotero remains in development as of October 2014. The latest commits can be found on the [dev branch][9]. If you encounter an error, please open an issue.

## Pull Requests ##

Pull requests are welcomed. Please read the [contribution guidelines](CONTRIBUTING.md). 

## Versioning ##
As of v1.0.0, Pyzotero is versioned according to [Semver](http://semver.org); version increments are performed as follows:  



1. MAJOR version will increment with incompatible API changes,
2. MINOR version will increment when functionality is added in a backwards-compatible manner, and
3. PATCH version will increment with backwards-compatible bug fixes.

# License #

Pyzotero is licensed under version 3 of the [GNU General Public License][8]. See `license.txt` for details.  

[1]: https://www.zotero.org/support/dev/web_api/v3/start
[2]: https://www.zotero.org/settings/keys/new
[3]: http://pyzotero.readthedocs.org/en/latest/
[4]: http://packages.python.org/Pyzotero/
[5]: http://feedparser.org
[6]: http://pypi.python.org/pypi/pip
[7]: https://nose.readthedocs.org/en/latest/
[8]: http://www.gnu.org/copyleft/gpl.html
[9]: https://github.com/urschrei/pyzotero/tree/dev
[10]: http://www.pip-installer.org/en/latest/index.html
† This isn't strictly true: you only need an API key for personal libraries and non-public group libraries.

