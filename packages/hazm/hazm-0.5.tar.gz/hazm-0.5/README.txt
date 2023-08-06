Hazm
====

Python library for digesting Persian text.

-  Text cleaning
-  Sentence and word tokenizer
-  Word lemmatizer
-  POS tagger
-  Shallow parser
-  Dependency parser
-  Interfaces for Persian corpora
-  `NLTK <http://nltk.org/>`__ compatible
-  Python 2.7, 3.2, 3.3 and 3.4 support
-  |Build Status|

Usage
-----

.. code:: python

    >>> from __future__ import unicode_literals
    >>> from hazm import *

    >>> normalizer = Normalizer()
    >>> normalizer.normalize('اصلاح نويسه ها و استفاده از نیم‌فاصله پردازش را آسان مي كند')
    'اصلاح نویسه‌ها و استفاده از نیم‌فاصله پردازش را آسان می‌کند'

    >>> sent_tokenize('ما هم برای وصل کردن آمدیم! ولی برای پردازش، جدا بهتر نیست؟')
    ['ما هم برای وصل کردن آمدیم!', 'ولی برای پردازش، جدا بهتر نیست؟']
    >>> word_tokenize('ولی برای پردازش، جدا بهتر نیست؟')
    ['ولی', 'برای', 'پردازش', '،', 'جدا', 'بهتر', 'نیست', '؟']

    >>> stemmer = Stemmer()
    >>> stemmer.stem('کتاب‌ها')
    'کتاب'
    >>> lemmatizer = Lemmatizer()
    >>> lemmatizer.lemmatize('می‌روم')
    'رفت#رو'

    >>> tagger = POSTagger(model='resources/postagger.model')
    >>> tagger.tag(word_tokenize('ما بسیار کتاب می‌خوانیم'))
    [('ما', 'PRO'), ('بسیار', 'ADV'), ('کتاب', 'N'), ('می‌خوانیم', 'V')]

    >>> chunker = Chunker(model='resources/chunker.model')
    >>> tagged = tagger.tag(word_tokenize('کتاب خواندن را دوست داریم'))
    >>> tree2brackets(chunker.parse(tagged))
    '[کتاب خواندن NP] [را POSTP] [دوست داریم VP]'

    >>> parser = DependencyParser(tagger=tagger, lemmatizer=lemmatizer)
    >>> parser.parse(word_tokenize('زنگ‌ها برای که به صدا درمی‌آید؟'))
    <DependencyGraph with 8 nodes>

Installation
------------

::

    pip install hazm

We have also trained `tagger and parser
models <http://dl.dropboxusercontent.com/u/90405495/resources.zip>`__.
You may put these models in the ``resources`` folder of your project.

Extensions
----------

-  `**JHazm** <https://github.com/mojtaba-khallash/JHazm>`__: A Java
   version of Hazm
-  `**NHazm** <https://github.com/mojtaba-khallash/NHazm>`__: A C#
   version of Hazm

Thanks
------

-  to constributors: `Mojtaba
   Khallash <https://github.com/mojtaba-khallash>`__ and `Mohsen
   Imany <https://github.com/imani>`__.
-  to `Virastyar <http://virastyar.ir/>`__ project for persian word
   list.

.. |Build Status| image:: https://travis-ci.org/sobhe/hazm.png
   :target: https://travis-ci.org/sobhe/hazm
