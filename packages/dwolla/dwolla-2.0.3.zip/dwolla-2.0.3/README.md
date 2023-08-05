dwolla-python
=========

[![Build Status](https://travis-ci.org/Dwolla/dwolla-python.svg?branch=master)](https://travis-ci.org/Dwolla/dwolla-python)

The new and improved Dwolla library based off of the Python `requests` client. `dwolla-python` includes support for all API endpoints, and is the new library officially supported by Dwolla.

## Version

2.0.3

## Installation

`dwolla-python` is available on [PyPi](https://pypi.python.org/pypi/dwolla), and therefore can be installed automagically via [pip](https://pip.pypa.io/en/latest/installing.html).

**The Python `requests` library is required for `dwolla-python` to operate. It is included as a dependency on this package if your environment does not already have it.**

*To install:*

```
pip install dwolla
```

*To add to `requirements.txt` and make this a permanent dependency of your package:*

```requirements.txt
YourApp
SomeLibrary==1.2.3
dwolla>=2.0.0
```

```
pip install -r requirements.txt
```

## Quickstart

`dwolla-python` makes it easy for developers to hit the ground running with our API. Before attempting the following, you should ideally create [an application key and secret](https://www.dwolla.com/applications).

* Change settings in `constants.py` by editing the file, or on-the-fly by doing `from dwolla import constants`, `constants.some_setting = some_value`.
* `from dwolla import module` where `module` is either `accounts`, `checkouts`, `contacts`, `fundingsources`, `masspay`, `oauth`, `request`, or `transactions`, or `from dwolla import *` to import all.
* Use at will!

### Example; Partial Import

`dwolla-python` allows you to import only the modules you need. 

*For this example, we will get information about a Dwolla ID.*

```python
from dwolla import accounts

print accounts.basic('812-121-7199')
```

### Example; Complete Import

`dwolla-python` also allows you to import the entire library to access everything at once.

*For this example, we will get information about a Dwolla ID, as well as request 5.00 from that same ID.*

```python
from dwolla import *

# Get information about the ID

print accounts.basic('812-121-7199')

# Request $5.00 from that ID

print request.create('812-121-7199', 5.00)
```

### Configuration and Use

Whenever you change settings, they will only be partially applied. This means that settings in `constants.py` will remain until they are changed. 

#### Default Settings
```python
client_id = 'YOUR ID HERE'
client_secret = 'YOUR SECRET HERE'
pin = 1234

oauth_scope = 'Send|Transactions|Balance|Request|Contacts|AccountInfoFull|Funding|ManageAccount'
access_token = 'OAUTH TOKENS GO HERE'

# Hostnames, endpoints
production_host = 'https://www.dwolla.com/'
sandbox_host = 'https://uat.dwolla.com/'
default_postfix = 'oauth/rest'

# Client behavior
sandbox = True
debug = True
host = None
rest_timeout = 15
proxy = False
```

#### Proxies

`dwolla-python` also supports proxies. In order to set proxies, you must assign a python dictionary to the proxy constant in the following format:

```
proxy = {
    'http': 'http://someproxy:someport',
    'https': 'https://anotherproxy:anotherport'
}
```

#### Example

**`customsettings.py` contains the following example in more detail.**

```python
# Import everything from the dwolla package
from dwolla import *

# Configure the library (change these)
constants.sandbox=False

constants.client_id = "zbDwIC0dWCVU7cQtfvGwVwVjvxwQfjaTgkVi+FZOmKqPBzK5JG"
constants.client_secret = "ckmgwJz9h/fZ09unyXxpupCyrmAMe0bnUiMHF/0+SDaR9RHe99"
constants.access_token = "aK6DdCVlIsR1hKvTbp8VCwnvci8cwaTLlW9edtbHJVmKoopnoe"


# Example 1: Get basic information for a user via
# their Dwolla ID.

print accounts.basic('812-202-3784')
```

### Override Settings

For endpoints that take either an `access_token` or a `pin`, it is possible to pass in alternate tokens or pins into those functions.

#### Example; Create a MassPay job

##### Function prototype
```python
def create(fundssource, items, params=False, alternate_token=False, alternate_pin=False):
```

```python
from dwolla import masspay

myItems = {...}

masspay.create('Balance', myItems, alternate_token="My Alternate Token", alternate_pin=1234)
```

---

There are 9 quick-start files which will walk you through working with `dwolla-python`'s classes/endpoint groupings.

* `customsettings.py`: Instantiate library with custom settings.
* `accounts.py`: Retrieve account information, such as balance.
* `checkouts.py`: Offsite-gateway endpoints, server-to-server checkout example.
* `contacts.py`: Retrieve/sort through user contacts.
* `fundingsources.py`: Modify and get information with regards to funding sources.
* `masspay.py`: Create and retrieve jobs/data regarding MassPay jobs.
* `oauth.py`: Examples on retrieving OAuth access/refresh token pairs.
* `request.py`: Create and retrieve money requests/information regarding money requests.
* `transactions.py`: Send money, get transaction info by ID, etc.

## Structure

`dwolla-python` is a conglomerate of multiple modules; each module in the `dwolla/` directory is named after a the endpoints that it covers ([similar to Dwolla's developer documentation](https://developers.dwolla.com/dev/docs)).

### Endpoint Modules and Methods

Each endpoint module depends on `Rest()` in `rest.py` to fulfill `GET` and `POST` requests.

* `accounts.py`:
 * `basic()`: Retrieves basic account information
 * `full()`: Retrieve full account information
 * `balance()`: Get user balance
 * `nearby()`: Get nearby users
 * `autowithdrawalstatus()`: Get auto-withdrawal status
 * `toggleautowithdrawalstatus()`: Toggle auto-withdrawal
* `checkouts.py`:
 * `create()`: Creates a checkout session.
 * `get()`: Gets status of existing checkout session.
 * `complete()`: Completes a checkout session.
 * `verify()`: Verifies a checkout session.
* `contacts.py`:
 * `get()`: Retrieve a user's contacts.
 * `nearby()`: Get spots near a location.
* `fundingsources.py`:
 * `info()`: Retrieve information regarding a funding source via ID.
 * `get()`: List all funding sources.
 * `add()`: Add a funding source.
 * `verify()`: Verify a funding source.
 * `withdraw()`: Withdraw from Dwolla into funding source.
 * `deposit()`: Deposit to Dwolla from funding source.
* `masspay.py`:
 * `create()`: Creates a MassPay job.
 * `getjob()`: Gets a MassPay job.
 * `getjobitems()`: Gets all items for a specific job.
 * `getitem()`: Gets an item from a specific job.
 * `listjobs()`: Lists all MassPay jobs.
* `oauth.py`:
 * `genauthurl()`: Generates OAuth permission link URL
 * `get()`: Retrieves OAuth + Refresh token pair from Dwolla servers.
 * `refresh()`: Retrieves OAuth + Refresh pair with refresh token.
* `request.py`:
 * `create()`: Request money from user.
 * `get()`: Lists all pending money requests.
 * `info()`: Retrieves info for a pending money request.
 * `cancel()`: Cancels a money request.
 * `fulfill()`: Fulfills a money request.
* `transactions.py`:
 * `send()`: Sends money
 * `refund()`: Refunds money
 * `get()`: Lists transactions for user
 * `info()`: Get information for transaction by ID.
 * `stats()`: Get transaction statistics for current user.

## Unit Testing

`dwolla-python` uses [unittest](https://docs.python.org/2/library/unittest.html) for unit testing. Integration testing is planned sometime in the future.

To run the tests, install `dwolla-python` as per the aforementioned instructions and run:

```
cd location/of/the/library
pip install unittest
python -m unittest discover tests/
```

## README

In order for the library's README file to display nicely on PyPi, we must use the `*.rst` file format. When making changes to this README file, please [use this tool](http://johnmacfarlane.net/pandoc/try/) to convert the `*.md` file to `*.rst`, and make sure to keep both files updated.

## Changelog

2.0.3
* Fixed OAuth handshake bug involving `redirect_uri` (thanks @melinath for the bug submission)!

2.0.2
* Added a webhooks module for `verify()` (thanks @mez).
* Fixed bug in offsite-gateway checkouts (also thanks, @mez!). 

2.0.1
* Added MANIFEST.in to resolve issues with README failing retrieval from PyPi.

2.0.0
* Initial release.

## Credits

This wrapper is based on [requests](http://docs.python-requests.org/) for REST capability and uses [unittest](https://docs.python.org/2/library/unittest.html) for unit testing and [Travis](https://travis-ci.org/) for automagical build verification.

Version `2.x` initially written by [David Stancu](http://davidstancu.me) (david@dwolla.com).

Versions `1.x`:
The old wrapper is a forked extension of Thomas Hansen's 'dwolla-python' module.

- Thomas Hansen &lt;thomas.hansen@gmail.com&gt;
- Jordan Bouvier &lt;jbouvier@gmail.com&gt;
- Michael Schonfeld &lt;michael@dwolla.com&gt;
- George Sibble &lt;george.sibble@ultapay.com&gt;
- Andrey Fedorov &lt;anfedorov@gmail.com&gt;

## License

Copyright (c) 2014 Dwolla Inc, David Stancu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
