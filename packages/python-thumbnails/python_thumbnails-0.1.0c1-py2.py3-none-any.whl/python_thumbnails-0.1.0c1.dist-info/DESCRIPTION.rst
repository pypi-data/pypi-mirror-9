python-thumbnails |Build status| |Coverage status|
==================================================

Thumbnails for Django, Flask and other Python projects.

Work in progress
----------------

This project is currently work in progress. It is not production ready.
`This gist <https://gist.github.com/relekang/1544815ce1370a0be2b4>`__
outlines the planned features and there status of them.

Install
-------

.. code:: bash

    pip install pillow  # default image engine, not necessary if another engine is used
    pip install python-thumbnails

Usage
-----

.. code:: python

    from thumbnails import get_thumbnail

    get_thumbnail('path/to/image.png', '300x300', 'center')

--------------

MIT © Rolf Erik Lekang

.. |Build status| image:: https://ci.frigg.io/badges/relekang/python-thumbnails/
   :target: https://ci.frigg.io/relekang/python-thumbnails/last/
.. |Coverage status| image:: https://ci.frigg.io/badges/coverage/relekang/python-thumbnails/
   :target: https://ci.frigg.io/relekang/python-thumbnails/last/


