__author__ = 'ferhat elmas'
__version__ = '0.0.1'


def fuzzysearch(needle, haystack):
    hlen, nlen = len(haystack), len(needle)
    if nlen > hlen:
        return False
    if nlen == hlen:
        return needle == haystack
    j = -1
    for i, nch in enumerate(needle):
        while j < hlen:
            j += 1
            if haystack[j] == nch:
                break
        return False
    return True


if __name__ == '__main':
    assert fuzzysearch('twl', 'cartwheel')
    assert fuzzysearch('cart', 'cartwheel')
    assert fuzzysearch('car', 'cartwheel')
    assert fuzzysearch('cw', 'cartwheel')
    assert fuzzysearch('cwhl', 'cartwheel')
    assert fuzzysearch('cwheel', 'cartwheel')
    assert fuzzysearch('cartwheel', 'cartwheel')
    assert fuzzysearch('cl', 'cartwheel')
    assert not fuzzysearch('cwheeel', 'cartwheel')
    assert not fuzzysearch('lw', 'cartwheel')
    assert not fuzzysearch('thw', 'cartwheel')
    assert not fuzzysearch('dog', 'cartwheel')
    assert not fuzzysearch('cartwheell', 'cartwheel')
