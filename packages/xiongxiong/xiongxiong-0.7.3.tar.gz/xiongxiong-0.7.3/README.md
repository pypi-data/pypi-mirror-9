# Xiongxiong Decoder

Bearer token decoder for Python (>= 2.7 and 3).

## Installation

Using `pip`:

    pip install xiongxiong

## `Xiongxiong` Class

The class *must* be instantiated with the private key and, optionally,
the hashing algorithm (defaults to `sha1`).

For example:

```python
from xiongxiong import Xiongxiong
xiongxiong = Xiongxiong(privateKey, 'md5')
```

n.b., An exception will be thrown if the specified hashing algorithm is
not supported. If you are using Python greater than 2.7.9 or 3.2, you
will have access to all the algorithms supported by your platform's
instance of OpenSSL; otherwise you are limited to MD5, SHA1, SHA224,
SHA256, SHA384 and SHA512.

Obviously, the private key and hashing algorithm must match those used
by a token's encoder in order to successfully decode it.

### `xiongxiong(accessToken)`
### `xiongxiong(basicLogin, basicPassword)`

An instantiation of the `Xiongxiong` class is callable and will decode
the seed data, expiration and validate from the bearer token/basic
authentication pair, returning a `Token` object (see below).

## `Token` Object

The decoded `Token` is built, called by the above function, in such a
way that its properties are read-only. (The factory function shouldn't
be invoked directly and has been designed to be a private module
function, insofar as Python allows.) It nonetheless has the following
members:

* `.data` The original seed data, which will be split into a list by `:`
  characters, wherever possible (a string, otherwise).
* `.expiration` The expiration time (`datetime.datetime`)
* `.valid` The validity of the token/basic pair (Boolean).

For example, continuing from the above:

```python
from datetime import datetime

tokenData = xiongxiong(someBearerToken)

if tokenData.valid:
  expiresIn = tokenData.expiration - datetime.now()
  print('Token expires in %d seconds.' % expiresIn.seconds)
  print('Contents: %s' % tokenData.data)
```

The validity property (`valid`) will return `false` if the token can't
be authenticated, otherwise it will test whether the token has passed
its best before date.
