=====
Emote
=====


.. image:: https://travis-ci.org/geowurster/Emote.svg?branch=master
    :target: https://travis-ci.org/geowurster/Emote


.. image:: https://coveralls.io/repos/geowurster/Emote/badge.svg?branch=master
    :target: https://coveralls.io/r/geowurster/Emote

Simple `emoji <http://www.unicode.org/Public/emoji/1.0/full-emoji-list.html>`__ lookups for Python.


Example
=======

.. code-block:: python

    import emote
    print(emote.lookup(':water_wave:'))
    🌊
    print(emote.decode('🌊'))
    water_wave


Installation
============

Via pip:

.. code-block:: console

    $ pip install emote --upgrade

From master branch:

.. code-block:: console

    $ git clone https://github.com/geowurster/Emote.git
    $ cd Emote
    $ python setup.py install


Developing
==========

.. code-block:: console

    $ git clone https://github.com/geowurster/Emote.git
    $ cd Emote
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -r requirements-dev.txt -e .
    $ nosetests --with-coverage


License
=======

See ``LICENSE.txt``.
