`dossier.fc` is a Python package that provides an implementation of feature
collections. Abstractly, a feature collection is a map from feature name to
a feature. While any type of feature can be supported, the core focus of this
package is on *multisets* or "bags of words" (BOW). In this package, the
default multiset implementation is a `StringCounter`, which maps Unicode
strings to counts.

This package also includes utilities for serializing and deserializating
collections of feature collections to CBOR (Concise Binary Object
Representation).


### Installation

`dossier.fc` is on PyPI and can be installed with `pip`:

```bash
pip install dossier.fc
```

Currently, `dossier.fc` requires Python 2.7. It is not yet Python 3 compatible.


### Documentation

API documentation with examples is available as part of the Dossier Stack
documentation:
[http://dossier-stack.readthedocs.org](http://dossier-stack.readthedocs.org#module-dossier.fc)


### Examples and basic usage

By default, feature collections use `StringCounter` for feature representation:

```python
from dossier.fc import FeatureCollection

fc = FeatureCollection()
fc['NAME']['alice'] += 1
fc['NAME']['bob'] = 5

print type(fc['NAME'])
# output: StringCounter
```

As the name suggests, a `StringCounter` is a subclass of the `Counter` class
found in the Python standard library `collections` module. As such, it supports
binary operations like addition, subtraction, equality testing, etc.
The `FeatureCollection` class also provides these binary operations which are
performed on corresponding features. For example:

```python
from dossier.fc import FeatureCollection

fc1 = FeatureCollection({'NAME': {'alice': 1, 'bob': 1}})
fc2 = FeatureCollection({'NAME': {'alice': 1}})
fc3 = fc1 + fc2

assert fc3 == FeatureCollection({'NAME': {'alice': 2, 'bob': 1}})
```
