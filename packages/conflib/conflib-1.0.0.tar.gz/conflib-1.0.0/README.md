conflib
=========

[![Latest Version](https://img.shields.io/pypi/v/conflib.svg)](https://pypi.python.org/pypi/conflib/)
[![Coverage Status](https://img.shields.io/coveralls/akerl/conflib.svg)](https://coveralls.io/r/akerl/conflib)
[![Build Status](https://img.shields.io/travis/akerl/conflib.svg)](https://travis-ci.org/akerl/conflib)
[![MIT Licensed](https://img.shields.io/badge/license-MIT-green.svg)](https://tldrlegal.com/license/mit-license)

Simplifies configuration stacking. Primarily, this was written to allow stacking of default, global, and local settings. It allows for validation so that you can enforce contraints on supplied options.

## Usage

Using conflib is just a matter of importing it and giving it some dictionaries to stack:

```
>>> import conflib
>>> Default = {'hello': 'world', 'alpha': 5}
>>> Global = {'wat': 'wut', 'fancy': (20, 'fish')}
>>> Local = {'hello': 'everybody', 'beta': 'qwerty'}
>>> Config = conflib.Config(Default, Global, Local)
>>> print(Config.options)
{'alpha': 5, 'wat': 'wut', 'beta': 'qwerty', 'hello': 'everybody', 'fancy': (20, 'fish')}
```

If you need to stack on new configs later, go for it:

```
>>> Config.stack({'wat': 'new_value', 'extra': 10})
>>> print(Config.options)
{'alpha': 5, 'wat': 'new_value', 'beta': 'qwerty', 'hello': 'everybody', 'fancy': (20, 'fish'), 'extra': 10}
```

Pass in a validation dictionary if you want to check the provided arguments:

```
Validator = {
    'alpha': lambda x: x < 10,
    'fancy': tuple,
    'beta': [('asdf', 'qwerty'), ('fizz','buzz')]
}
Config.validate(Validator)
```

Alternately, you can pass in a validation\_dict when creating a Config object. Validation failures raise ValueError with a message indicating the specific failure. There are several available options for the Validation dictionary:

* `bool`: Converts 'y', 'yes', '1', 1, and True to True, and 'n', 'no', '0', 0 and False to False
* `int`: Casts provided value as an integer
* A list of tuples: looks for the provided value as a member of any of the tuples, and returns the first item in that tuple
* A list: looks for the provided value in the list
* Any type (`str`, `float`, etc): validates that the provided value is of the specified type (does not try to cast it)
* A callable: Runs the provided function, which should either return the validated value or raise TypeError

## Installation

    pip install conflib

## License

conflib is released under the MIT License. See the bundled LICENSE file for details.

