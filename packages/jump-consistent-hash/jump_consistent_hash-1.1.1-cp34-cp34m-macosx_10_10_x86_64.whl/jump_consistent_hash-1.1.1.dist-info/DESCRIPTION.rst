
Jump Consistent Hash
--------------------

Python (3) implementation of the jump consistent hash algorithm by John Lamping
and Eric Veach[1].

Usage
`````

.. code:: python
    >>> import jump
    >>> jump.hash(256, 1024)
    520

Or if you want to use the C++ extension:

.. code:: python
    >>> jump.fasthash(256, 1024)
    520

Links
`````

[1] http://arxiv.org/pdf/1406.2294v1.pdf



