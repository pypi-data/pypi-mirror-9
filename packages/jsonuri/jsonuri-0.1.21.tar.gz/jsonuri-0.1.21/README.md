
JSONURI-PY
==============
 
This package helps you convert Python dictionaries into an HTTP GET request parameters, and vice-versa. 

An example of a practical application would be to send JSON data over HTTP GET, e.g. to a static resource small.png, and harvest the data from access logs instead of running real-time data collection.

**Note**: You should avoid send sensitive information using this mechanism, or at least ensure you send your data over SSL.

Equivalent libs/packages:
==========================

* JavaScript: [jsonuri-js](https://bitbucket.org/guidj/jsonuri-js)
* PHP: [jsonuri-php](https://bitbucket.org/guidj/jsonuri-php)

Examples:
=============

Serialization:
---------------

```python
>>> import json
>>> import urllib.parse
>>> from jsonuri import jsonuri
>>> jsonuri.serialize(json.loads('{"age": "31", "name": "John"}'))
'age%3D31%26name%3DJohn'
>>> jsonuri.serialize(json.loads('{"age": "31", "name": "John"}'), encode=False)
'age=31&name=John'
```

Desirialization
----------------

```python
>>> string = "name=John&age=31" # or "name%3DJohn%26age%3D31"
>>> jsonuri.deserialize(string)
{'age': '31', 'name': 'John'}
```

Notes
======

The package was not designed to process HTML form data, specifically multi-value variables, i.e. from select attributes. Though if you convert the data to a JSON/JavaScript object, that should work.