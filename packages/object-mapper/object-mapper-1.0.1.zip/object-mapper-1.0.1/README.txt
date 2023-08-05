# Object Mapper

**Version**
1.0.0-draft

**Author**
marazt

**Copyright**
marazt

**License**
The MIT License (MIT)

**Last updated**
12 February 2015

**Package Download**
https://pypi.python.org/pypi/object-mapper/1.0.0
---

## About

**ObjectMapper** is a class for automatic object mapping inspired by .NET **AutoMapper**.
It helps you to create objects between project layers (data layer, service layer, view) in a simple, transparent way.

## Example

1.  **Mapping of the properties without mapping definition**

In this case are mapped only these properties of the target class which
are in target and source classes. Other properties are not mapped.
Suppose we have class `A` with attributes `name` and `last_name`
and class `B` with attribute `name`.
Initialization of the ObjectMapper will be:

```python
mapper = ObjectMapper()
mapper.create_map(A, B)
instance_b = mapper.map(A())
```

In this case, value of A.name will be copied into B.name.

2. **Mapping with defined mapping functions**

Suppose we have class `A` with attributes `first_name` and `last_name`
, class `B` with attribute `full_name` and class `C` with attribute reverse_name.
And want to map it in a way `B.full_name = A.first_name + A.last_name` and
`C.reverse_name = A.last_name + A.first_name`
Initialization of the ObjectMapper will be:

```python
mapper = ObjectMapper()
mapper.create_map(A, B, {'name': lambda a : a.first_name + " " + a.last_name})
mapper.create_map(A, C, {'name': lambda a : a.last_name + " " + a.first_name})

instance_b = mapper.map(A())
instance_c = mapper.map(A())
```

In this case, to the `B.name` will be mapped `A.first_name + " " + A.last_name`
In this case, to the `C.name` will be mapped `A.last_name + " " + A.first_name`

3. **Mapping suppression**

For some purposes, it can be needed to suppress some mapping.
Suppose we have class `A` with attributes `name` and `last_name`
and class `B` with attributes `name` and `last_name`.
And we want to map only the `A.name` into `B.name`, but not `A.last_name` to
`B.last_name`
Initialization of the ObjectMapper will be:

```python
mapper = ObjectMapper()
mapper.create_map(A, B, {'last_name': None})

instance_b = mapper.map(A())
```

In this case, value of A.name will be copied into `B.name` automatically by the attribute name `name`.
Attribute `A.last_name` will be not mapped thanks the suppression (lambda function is None).

**Note:** You can find more examples in tests package

## Installation

* Download this project
* Download fro Pypi: https://pypi.python.org/pypi/object-mapper/1.0.0 

### ENOJOY IT!