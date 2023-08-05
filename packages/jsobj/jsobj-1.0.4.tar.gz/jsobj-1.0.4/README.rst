jsobj: JavaScript-Style Objects in Python
=========================================

jsobj provides JavaScript-Style Objects in Python. It is based on jsobject, but returns None if you try accessing non-existent keys instead of throwing an exception.

Homepage and documentation: https://github.com/gkovacs/jsobj


Example: "Hello World" with jsobj
---------------------------------

.. code-block:: python

  from jsobject import Object
  data = {
    "boolean": True,
    "null": None,
    "number": 123,
    "objectA": {'a': 'b', 'c': {'d': 'e', 'f': {'g': 'h'}}}
    }

  jso = Object(data)

  print(jso.boolean)       # True
  print(jso.null)          # None
  print(jso.number)        # 123
  print(jso.objectA)       # {'a': 'b', 'c': {'d': 'e', 'f': {'g': 'h'}}}
  print(jso.objectA.a)     # b
  print(jso.objectA.c.d)   # e
  print(jso.objectA.c.f.g) # h


Installation
------------
::

  $ pip install jsobj


License
-------

MIT


Credits
-------

`Geza Kovacs <https://github.com/gkovacs>`_. Based on jsobject by Marcin Wierzbanowski
