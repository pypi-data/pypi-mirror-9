===============
awesome-slugify
===============
.. image:: https://travis-ci.org/dimka665/awesome-slugify.svg?branch=master
    :target: https://travis-ci.org/dimka665/awesome-slugify

**Python flexible slugify function**

| PyPi: https://pypi.python.org/pypi/awesome-slugify
| Github: https://github.com/dimka665/awesome-slugify


Install
=======
.. code-block:: bash

    pip install awesome-slugify

Usage
=====

.. code-block:: python

    from slugify import slugify

    slugify('Any text')  # 'Any-text'

Custom slugify
==============

.. code-block:: python

    from slugify import slugify, Slugify, UniqueSlugify

    slugify('Any text', to_lower=True)  # 'any-text'

    custom_slugify = Slugify(to_lower=True)
    custom_slugify('Any text')          # 'any-text'

    custom_slugify.separator = '_'
    custom_slugify('Any text')          # 'any_text'

    custom_slugify = UniqueSlugify()
    custom_slugify('Any text')          # 'any-text'
    custom_slugify('Any text')          # 'any-text-1'

slugify function optional args
------------------------------

.. code-block:: python

    to_lower              # if True convert text to lowercase
    max_length            # output string max length
    separator             # separator string
    capitalize            # if True upper first letter


Slugify class args
------------------

.. code-block:: python

    pretranslate = None               # function or dict for replace before translation
    translate = unidecode.unidecode   # function for slugifying or None
    safe_chars = ''                   # additional safe chars
    stop_words = ()                   # remove these words from slug

    to_lower = False                  # default to_lower value
    max_length = None                 # default max_length value
    separator = '-'                   # default separator value
    capitalize = False                # default capitalize value

UniqueSlugify class args
------------------------

.. code-block:: python

    # all Slugify class args +
    uids = []                         # initial unique ids

Predefined slugify functions
============================

Some slugify functions is predefined this way:

.. code-block:: python

    from slugify import Slugify, CYRILLIC, GERMAN, GREEK

    slugify = Slugify()
    slugify_unicode = Slugify(translate=None)

    slugify_url = Slugify()
    slugify_url.to_lower = True
    slugify_url.stop_words = ('a', 'an', 'the')
    slugify_url.max_length = 200

    slugify_filename = Slugify()
    slugify_filename.separator = '_'
    slugify_filename.safe_chars = '-.'
    slugify_filename.max_length = 255

    slugify_ru = Slugify(pretranslate=CYRILLIC)
    slugify_de = Slugify(pretranslate=GERMAN)
    slugify_el = Slugify(pretranslate=GREEK)

Examples
========

.. code-block:: python

    from slugify import Slugify, UniqueSlugify, slugify, slugify_unicode
    from slugify import slugify_url, slugify_filename
    from slugify import slugify_ru, slugify_de

    slugify('one kožušček')                       # one-kozuscek
    slugify('one two three', separator='.')       # one.two.three
    slugify('one two three four', max_length=12)  # one-two-four   (12 chars)
    slugify('one TWO', to_lower=True)             # one-two
    slugify('one TWO', capitalize=True)           # One-TWO

    slugify_filename(u'Дrаft №2.txt')             # Draft_2.txt
    slugify_url(u'Дrаft №2.txt')                  # draft-2-txt

    my_slugify = Slugify()
    my_slugify.separator = '.'
    my_slugify.pretranslate = {'я': 'i', '♥': 'love'}
    my_slugify('Я ♥ борщ')                        # I.love.borshch  (custom translate)

    slugify('Я ♥ борщ')                           # Ia-borshch  (standard translation)
    slugify_ru('Я ♥ борщ')                        # Ya-borsch   (alternative russian translation)
    slugify_unicode('Я ♥ борщ')                   # Я-борщ      (sanitize only)

    slugify_de('ÜBER Über slugify')               # UEBER-Ueber-slugify

    slugify_unique = UniqueSlugify(separator='_')
    slugify_unique('one TWO')                     # One_TWO
    slugify_unique('one TWO')                     # One_TWO_1

    slugify_unique = UniqueSlugify(uids=['cellar-door'])
    slugify_unique('cellar door')                 # cellar-door-1


Custom Unique Slugify Checker
=============================

.. code-block:: python

    from slugify import UniqueSlugify

    def my_unique_check(text, uids):
        if text in uids:
            return False
        return not SomeDBClass.objects.filter(slug_field=text).exists()

    custom_slugify_unique = UniqueSlugify(unique_check=my_unique_check)

    # Checks the database for a matching document
    custom_slugify_unique('te occidere possunt')


Running UnitTests
=================

.. code-block:: bash

    $ virtualenv venv
    $ venv/bin/pip install -r requirements.txt
    $ venv/bin/nosetests slugify
