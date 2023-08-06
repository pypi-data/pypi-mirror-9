# -- encoding: utf-8 --
"""

SciSerialize
============
A format for serializing scientific data.

An initial python implementation -- in dev status.

This module implements type encoders and decoders combined with
`msgpack` and `json` to serialize data-types often used in scientific
computations or engineering. So it can be used to serialize data to
MessagePack or JSON files for example.
All supported types can be serialized and can be deserialized to the
original types in python.
If a type is not supported, the option for enabling pickle is given.
This pickle option is for python internal use only!

The main goals of this module are to provide easy extensability, to be
verbose and to be elegant as possible:

For supporting a custom type, only a class with the attributes
`type_`, `typestr`, `encode` and `decode` must be implemented and
an instance can be added to the `TYPE_CODER_LIST`.
Example of a coder to support serialization of propper datetime
with timezone:
```python
class DateTimeIsoStringCoder(TypeCoder):
    from datetime import datetime
    import dateutil.parser
    type_ = datetime
    typestr = 'datetime'
    def encode(self, obj):
        return {TYPE_KEY: self.typestr,
                'isostr': self.datetime.isoformat(obj)}
    def decode(self, data):
        return self.dateutil.parser.parse(data['isostr'])
```

The encoded output is:

```
{"~#type": "datetime",
 "isostr": "2014-12-24T05:55:55.555+00"}
```

Example
-------
```python
from datetime import datetime
import numpy as np

import sciserialize as scs


data = [[datetime.today()],
         datetime.today()- datetime.today(),
         np.random.randn(3), {'Hallo'}]

packed = scs.packb(data, enable_pickle=True)
packed
Out[33]: "\x94\x91\x82\xc4\x06isostr\xc4\x1a2014-11-20T17:10:07.396000\xc4
\x06~#type\xc4\x08datetime\x84\xc4\x07seconds\x00\xc4\x08microsec\x00\xc4
\x04days\x00\xc4\x06~#type\xc4\ttimedelta\x84\xc4\x05dtype\xc4\x07float64\xc4
\x05shape\x91\x03\xc4\x05bytes\xc4\x18\xe7g\x80 \xb7B\xf3\xbfXGW~\xd9\xef
\xf9\xbfQ\xf8zg\n@\xf3\xbf\xc4\x06~#type\xc4\x07ndarray\x82\xc4\x01b
\xc40c__builtin__\nset\np0\n((lp1\nS'Hallo'\np2\natp3\nRp4\n.\xc4\x06~#type\xc4
\x08pypickle"

unpacked = scs.unpackb(packed, enable_pickle=True)
unpacked
Out[32]:
[[datetime.datetime(2014, 11, 20, 17, 10, 7, 396000)],
 datetime.timedelta(0),
 array([-1.20378792, -1.62105703, -1.20313492]),
 {'Hallo'}]

for d, u in zip(data, unpacked): print(d==u)
True
True
[ True  True  True]
True

```

Notes
-----
Be aware of floating point precision in JSON, if you need exactly the same
bytes as jour original object, this could be a problem!
Just use numpy arrays if you wand to avoid this problem in JSON.
In MessagePAck this is not a problem.

TODO:
Check out further data types to be implemented.

"""

import sciserialize.coders as coders
import sciserialize.serializers as serializers
from sciserialize.serializers import (dumps, loads, packb, unpackb,
                                      dump, load, pack, unpack)


__all__ = ['dumps', 'loads', 'packb', 'unpackb',
           'dump', 'load', 'pack', 'unpack',
           'coders', 'serializers']

__version__ = '0.1.1alpha'
