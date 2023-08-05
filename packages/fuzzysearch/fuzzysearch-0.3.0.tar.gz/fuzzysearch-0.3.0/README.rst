===============================
fuzzysearch
===============================

.. image:: https://badge.fury.io/py/fuzzysearch.png
    :target: http://badge.fury.io/py/fuzzysearch

.. image:: https://travis-ci.org/taleinat/fuzzysearch.png?branch=master
        :target: https://travis-ci.org/taleinat/fuzzysearch

.. image:: https://coveralls.io/repos/taleinat/fuzzysearch/badge.png?branch=master
        :target: https://coveralls.io/r/taleinat/fuzzysearch?branch=master

.. image:: https://pypip.in/d/fuzzysearch/badge.png
        :target: https://crate.io/packages/fuzzysearch?version=latest

fuzzysearch is useful for finding approximate subsequence matches

* Free software: `MIT license <LICENSE>`_
* Documentation: http://fuzzysearch.rtfd.org.

Installation
------------
Just install using pip::

    $ pip install fuzzysearch

Features
--------

* Fuzzy sub-sequence search: Find parts of a sequence which match a given
  sub-sequence up to a given maximum Levenshtein distance.
* Set individual limits for the number of substitutions, insertions and/or
  deletions allowed for a near-match.
* Includes optimized implementations for specific use-cases, e.g. only allowing
  substitutions in near-matches.

Simple Example
--------------
You can usually just use the `find_near_matches()` utility function, which
chooses a suitable fuzzy search implementation according to the given
parameters:

.. code:: python

    >>> from fuzzysearch import find_near_matches
    >>> find_near_matches('PATTERN', 'aaaPATERNaaa', max_l_dist=1)
    [Match(start=3, end=9, dist=1)]

Advanced Example
----------------
If needed you can choose a specific search implementation, such as
`find_near_matches_with_ngrams()`:

.. code:: python

    >>> sequence = '''\
    GACTAGCACTGTAGGGATAACAATTTCACACAGGTGGACAATTACATTGAAAATCACAGATTGGTCACACACACA
    TTGGACATACATAGAAACACACACACATACATTAGATACGAACATAGAAACACACATTAGACGCGTACATAGACA
    CAAACACATTGACAGGCAGTTCAGATGATGACGCCCGACTGATACTCGCGTAGTCGTGGGAGGCAAGGCACACAG
    GGGATAGG'''
    >>> subsequence = 'TGCACTGTAGGGATAACAAT' #distance 1
    >>> max_distance = 2

    >>> from fuzzysearch import find_near_matches_with_ngrams
    >>> find_near_matches_with_ngrams(subsequence, sequence, max_distance)
    [Match(start=3, end=24, dist=1)]
