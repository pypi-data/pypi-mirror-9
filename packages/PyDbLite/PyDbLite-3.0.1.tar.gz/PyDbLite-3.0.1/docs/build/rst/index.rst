
PyDbLite
********

PyDbLite is

* a fast, pure-Python, untyped, in-memory database engine, using
  Python syntax to manage data, instead of SQL

* a pythonic interface to SQLite using the same syntax as the
  pure-Python engine for most operations (except database connection
  and table creation because of each database specificities)

PyDbLite is suitable for a small set of data where a fully fledged DB
would be overkill.

Supported Python versions: 2.6+


Installation
============


PIP
---

::

   pip install pydblite


Manually
--------

Download the source and execute

::

   python setup.py install

* `Pure-Python engine <pythonengine.rst>`_
  * `Create or open a database
    <pythonengine.rst#create-or-open-a-database>`_
  * `Insert, update, delete a record
    <pythonengine.rst#insert-update-delete-a-record>`_
    * `insert a new record <pythonengine.rst#insert-a-new-record>`_
  * `Selection <pythonengine.rst#selection>`_
    * `to iterate on all the records
      <pythonengine.rst#to-iterate-on-all-the-records>`_
    * `Direct access <pythonengine.rst#direct-access>`_
    * `Simple selections <pythonengine.rst#simple-selections>`_
  * `List comprehension <pythonengine.rst#list-comprehension>`_
  * `Index <pythonengine.rst#index>`_
  * `Other attributes and methods
    <pythonengine.rst#other-attributes-and-methods>`_
* `SQLite adapter <sqliteengine.rst>`_
  * `Database <sqliteengine.rst#database>`_
  * `Table <sqliteengine.rst#table>`_
    * `Type conversion <sqliteengine.rst#type-conversion>`_
    * `cursor and commit <sqliteengine.rst#cursor-and-commit>`_
* `API <api.rst>`_
  * `PyDbLite.PyDbLite API <api.rst#module-pydblite.pydblite>`_
  * `PyDbLite.SQLite API <api.rst#module-pydblite.sqlite>`_
  * `PyDbLite.common API <api.rst#module-pydblite.common>`_
* `Example code
  <http://pydblite.readthedocs.org/en/latest/examples.html>`_
  * `Pure Python <examples.rst#pure-python>`_
  * `SQLite <examples.rst#sqlite>`_

Indices and tables
******************

* `Index <genindex.rst>`_

* `Module Index <py-modindex.rst>`_

* `Search Page <search.rst>`_
