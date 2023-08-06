# mutablerecords

Mutable records

## mutablerecords.Record

This is similar to collections.namedtuple, except it supports optional
attributes and mutability. A class definition is generated (with \__slots__,
\__str__ and other niceties), and can be used to instantiate new records of
that type. The record can also be subclassed to add new attributes or to add
methods to that data.

Sometimes, a Record definition is used to replace a simple \__init__ method
that only takes N arguments and sets them as instance variables. These
\__init__ methods are tedious to write and, even if you do, you still have
to write str, hash, eq functions, and set \__slots__ to be fully correct, but
who has the time for that? With records, you get all of that in a single
declaration, which you can even inline as your base class.

```python
# This acts like a mutable namedtuple, taking the same arguments.
Simple = records.Record('Simple', ['foo'])

# Now let's use a default argument.
SecondRecord = records.Record('SecondRecord', ['attr1', 'attr2'], attr3=0)
foo = SecondRecord(1, 2, attr3=3)
# str(foo) --> 'SecondRecord(attr1=1, attr2=2, attr3=3)'
bar = SecondRecord(attr1=1, attr2=2, attr3=5)
# str(bar) --> 'SecondRecord(attr1=1, attr2=2, attr3=5)'

class Third(SecondRecord):
    required_attributes = ['third1']
    optional_attributes = {'third2': 5}

# Third requires attr1, attr2, and third1.
baz = Third(1, 2, 3, third2=4)
# Here, second1 is required, so it goes before attr3:
# str(baz) --> 'Third(attr1=1, attr2=2, third1=3, attr3=0, third2=5)'

class OptionalMaker(records.Record('Required', ['required'])):
    required = None
    required_attributes = ['other']

opt = OptionalMaker(1)
# OptionalMaker has a class attribute that matches the name of a
#   required_attribute (required), so it becomes an optional_attribute with a
#   default equal to the attribute value (None). It also defines a new
#   required attribute 'other', which is set in opt as 1:
# str(opt) --> 'OptionalMaker(other=1, required=None)'
opt2 = OptionalMaker(2, required=3)
# This time, opt2 has required set, too, which is still an attribute.
# str(opt2) --> 'OptionalMaker(other=2, required=3)'
```

## mutablerecords.HashableRecord

All this does is add a __hash__ implementation for when the record will be
hashed, such as when a key in a `dict` or in a `set`.
