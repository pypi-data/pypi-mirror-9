wotwraper
========

A python library to wrap python objects onto Wotio

About
-----

Most APIs are wrapped in python as classes, of which you'd instantiate an object and call it's methods. This library wraps those functions onto the Wotio environment, allowing you to publish data to it, and access the API via s-expressions in JSON.

Example:

```python
class MyClass(object):
	def somefunc(self, param):
		return "Function called with parameter: {0}".format(param)
	def getdata(self):
		return "Some Data"
```

Those functions then become available on the bus using the JSON arrays:

```javascript
["somefunc","param"]
["getdata"]
```

In addition, a function can be used to publish data onto the bus consistently. The wrapper contains a loop that will call a specific function and publish its data periodically. More info below.

Getting Started
---------------

To install, run:

```shell
pip install wotwrapper
```

To use it, include it in your project and wrap an object:

```python
import wotwrapper
from phue import Bridge

b = Bridge('192.168.24.10')
wotwrapper.connect('http://wot.io/account/path', b, b.get_api, 10)

```

Parameters
----------

```python
wotwrapper.connect(path, objectToWrap, sendDataFunction, delay)
```

- **path:** This is the path for either the HTTP or Websocket endpoint that will be connected to. The path is in the format: `(http|ws)://host/account/in_exchange/in_key/in_queue/out_exchange/out_key/token`

- **objectToWrap:** This is the obejct to be wrapped.

- **sendDataFunction:** This is the function that provides the data to be published. Note that it does not have to be part of the same object.

- **delay:** This specifies the delay, in seconds, between the data publishing loop iterations.
