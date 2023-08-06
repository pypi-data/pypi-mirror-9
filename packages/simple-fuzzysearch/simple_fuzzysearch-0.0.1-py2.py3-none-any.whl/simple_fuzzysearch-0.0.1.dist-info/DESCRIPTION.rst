===========
fuzzysearch
===========

> Tiny and blazing-fast fuzzy search in Python

Fuzzy searching allows for flexibly matching a string with partial input, useful for filtering data very quickly based on lightweight user input.

Port of fuzzysearch in JavaScript https://github.com/bevacqua/fuzzysearch into Python.

Install
=======

    $ pip install simple-fuzzysearch

fuzzysearch(needle, haystack)
=============================

Returns true if needle matches haystack using a fuzzy-searching algorithm.
Note that this program doesn't implement levenshtein distance, but rather a simplified version where there's no approximation.
The method will return true only if each character in the needle can be found in the haystack and occurs after the preceding matches.


    fuzzysearch('twl', 'cartwheel') // <- true
    fuzzysearch('cart', 'cartwheel') // <- true
    fuzzysearch('cw', 'cartwheel') // <- true
    fuzzysearch('ee', 'cartwheel') // <- true
    fuzzysearch('art', 'cartwheel') // <- true
    fuzzysearch('eeel', 'cartwheel') // <- false
    fuzzysearch('dog', 'cartwheel') // <- false

License
=======

MIT



