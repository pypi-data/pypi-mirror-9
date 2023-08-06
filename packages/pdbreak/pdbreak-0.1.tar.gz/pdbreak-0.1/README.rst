pdbreak
=======

A quick break to your python script.

Usage
-----

.. code:: py

    #!/usr/bin/env python
    # encoding: utf-8
    print 1
    import pdbreak # import pdb;pdb.set_trace()
    print 2

Run your script

.. code:: sh

    $ python test.py
    1
    --Return--
    (Pdb) n
    > /home/lyc/github/pdbreak/test.py(6)<module>()
    -> print 2
    (Pdb) l
    1       #!/usr/bin/env python
    2       # encoding: utf-8
    3
    4       print 1
    5       import pdbreak
    6  ->   print 2
    [EOF]

