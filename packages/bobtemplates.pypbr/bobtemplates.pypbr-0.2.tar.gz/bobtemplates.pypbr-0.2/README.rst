bobtemplates to create python packages with pbr
===============================================

Creating python packages that use pbr_ via `mr.bob`_

Install
-------

.. code-block:: bash
   
   $ pip install bobtemplates.pypbr


Usage
-----

.. code-block:: txt
   
   mrbob bobtemplates.pypbr:package
   ...
   mrbob bobtemplates.pypbr:namespace_package


Variables
---------

Set in ``~/.mrbob``

.. code-block:: ini
   
   [variables]
   user.name = My Name
   user.email = my.name@example.com
   user.homepage = http://www.example.com/


You will be asked for the relevant values anyway, but the default values of
the fields will be the defined ones.

If these variables are not defined, they are queried via git.
mr.bob will ask you for this variables, and recommend the configured ones for
default.


There are more variables you could configure, and which are used in the header
of setup.py. Again this could be done in ``~/.mrbob`` or git.

.. code-block:: ini
   
   [variables]
   ...
   user.copyright_name = Your Company
   user.copyright_year = 2014



If user.copyright_name is not set, author name is used. If user.copyright_year
is not set, the current year is used.


Templates
---------

python\_package
```````````````

Usual python package with pbr_

.. code-block:: txt
   
   python-simple_package
   python-simple_package/.gitignore
   python-simple_package/LICENSE
   python-simple_package/MANIFEST.in
   python-simple_package/README.rst
   python-simple_package/setup.cfg
   python-simple_package/setup.py
   python-simple_package/simple_package
   python-simple_package/simple_package/__init__.py


python\_namespace\_package
``````````````````````````

python namspace package with pbr_

.. code-block:: txt
   
   python-simple-namespace
   python-simple-namespace/.gitignore
   python-simple-namespace/LICENSE
   python-simple-namespace/MANIFEST.in
   python-simple-namespace/README.rst
   python-simple-namespace/setup.cfg
   python-simple-namespace/setup.py
   python-simple-namespace/simple
   python-simple-namespace/simple/__init__.py
   python-simple-namespace/simple/namespace
   python-simple-namespace/simple/namespace/__init__.py


Known issues
------------

Recommendation of name etc. from git does not work on python < 2.7



mr.bob does not install as a requirement with ``pip < 6``. Consider to
mr.bob by hand.

.. code-block:: bash
   
   $ pip install mr.bob
   $ pip install bobtemplates.pypbr

.. _pbr: http://docs.openstack.org/developer/pbr/
.. _`mr.bob`: https://pypi.python.org/pypi/mr.bob/
