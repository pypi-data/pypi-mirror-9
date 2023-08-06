from datetime import date
from flatland import (
    Array,
    DateYYYYMMDD,
    Dict,
    Integer,
    Schema,
    List,
    )
from flatland.schema.paths import (
    NAME,
    SLICE,
    TOP,
    UP,
    HERE,
    pathexpr,
    tokenize,
    )
from tests._util import assert_raises


def _tokenizes_as(path, expected):
    tokenized = tokenize(path)
    assert tokenized == expected


top = (TOP, None)
up = (UP, None)
here = (HERE, None)
name = lambda x: (NAME, x)
sl = lambda x: (SLICE, x)


def test_tokenize():
    _tokencases = [
        (u'.', [here]),
        (u'/', [top]),
        (u'..', [up]),
        (u'/..', [top]),
        (u'../..', [up, up]),
        (u'//', [top, name(None)]),
        (u'foo', [name(u'foo')]),
        (u'/foo', [top, name(u'foo')]),
        (u'foo/', [name(u'foo')]),
        (u'foo/bar', [name(u'foo'), name(u'bar')]),
        (u'foo/../bar', [name(u'bar')]),
        (u'foo/./bar', [name(u'foo'), name(u'bar')]),
        (u'foo/./bar/.', [name(u'foo'), name(u'bar')]),
        (u'foo/bar[bogus]', [name(u'foo'), name(u'bar[bogus]')]),
        (u'a[b][c:d][0]', [name(u'a[b][c:d]'), name(u'0')]),
        (u'.[1]', [name(u'1')]),
        (u'foo[1]', [name(u'foo'), name(u'1')]),
        (u'foo[1]/', [name(u'foo'), name(u'1')]),
        (u'./foo[1]/', [name(u'foo'), name(u'1')]),
        (u'foo[1][2][3]', [name(u'foo'), name(u'1'), name(u'2'), name(u'3')]),
        (u'[1][2][3]', [name(u'1'), name(u'2'), name(u'3')]),
        (u'[1]/foo/[2]', [name(u'1'), name(u'foo'), name(u'2')]),
        (u'[:]', [sl(slice(None))]),
        (u'[1:]', [sl(slice(1, None))]),
        (u'[1:2]', [sl(slice(1, 2))]),
        (u'[:5]', [sl(slice(0, 5))]),
        (u'[-5:]', [sl(slice(-5, None))]),
        (u'[1:8:2]', [sl(slice(1, 8, 2))]),
        ]
    for path, expected in _tokencases:
        yield _tokenizes_as, path, expected


def test_tokenize_escapes():
    _tokencases = [
        (u'\\.', [name(u'.')]),
        (u'\\/', [name(u'/')]),
        (u'\\.\\.', [name(u'..')]),
        (u'/\\.\\.', [top, name(u'..')]),
        (u'\\/..', [name(u'/..')]),
        (u'..\\/..', [name(u'../..')]),
        (u'foo\\[1]', [name(u'foo[1]')]),
        (u'foo\\/bar', [name(u'foo/bar')]),
        (u'\\/foo', [name(u'/foo')]),
        (u'foo\\/', [name(u'foo/')]),
        ]
    for path, expected in _tokencases:
        yield _tokenizes_as, path, expected


class Mixed(Schema):
    i1 = Integer.using(default=0)

    d1 = Dict.of(Integer.named(u'd1i1').using(default=1),
                 Integer.named(u'd1i2').using(default=2))

    l1 = List.using(default=2).of(Integer.named(u'l1i1').using(default=3))

    l2 = List.using(default=3).of(Integer.named(u'l2i1').using(default=4),
                                  Integer.named(u'l2i2').using(default=5))

    l3 = List.using(default=2).of(
        List.named(u'l3l1').using(default=2).of(Integer.using(default=6)))

    a1 = Array.using(default=[10, 11, 12, 13, 14, 15]).of(Integer)

    dt1 = DateYYYYMMDD.using(default=date.today())


def _finds(el, path, expected):
    finder = pathexpr(path)
    elements = finder(el)
    found = [e.value for e in elements]

    if isinstance(expected, set):
        found = set(found)
    assert found == expected


def test_evaluation():
    el = Mixed.from_defaults()
    today = date.today()

    _finders = [
        (el[u'i1'], u'.', [0]),
        (el, u'i1', [0]),
        (el, u'/i1', [0]),
        (el, u'../i1', [0]),
        (el, u'../i1/.', [0]),
        (el[u'i1'], u'../i1', [0]),
        (el, u'd1/d1i1', [1]),
        (el, u'/d1/d1i2', [2]),
        (el[u'd1'][u'd1i1'], u'..', [{u'd1i1': 1, u'd1i2': 2}]),
        (el, u'/l1', [[3, 3]]),
        (el, u'/l1[:]', [3, 3]),
        (el, u'/l1[2:]', []),
        (el, u'/l1[0]', [3]),
        (el, u'./l1[0]', [3]),
        (el, u'l1/.[0]', [3]),
        (el, u'/l2[:]/l2i1', [4, 4, 4]),
        (el, u'/l3[:]', [[6, 6], [6, 6]]),
        (el, u'/l3[:][:]', [6, 6, 6, 6]),
        (el, u'l3[1:][1:]', [6]),
        (el, u'a1[1:]', [11, 12, 13, 14, 15]),
        (el, u'a1[:-1]', [10, 11, 12, 13, 14]),
        (el, u'a1[3]', [13]),
        (el, u'a1[2]', [12]),
        (el, u'a1[1]', [11]),
        (el, u'a1[0]', [10]),
        (el, u'a1[-1]', [15]),
        (el, u'a1[-2]', [14]),
        (el, u'a1[-3]', [13]),
        (el, u'a1[10]', []),
        (el, u'a1[-10]', []),
        (el, u'a1[-3:-1]', [13, 14]),
        (el, u'a1[1:3]', [11, 12]),
        (el, u'a1[:3]', [10, 11, 12]),
        (el, u'a1[::2]', [10, 12, 14]),
        (el, u'a1[2::2]', [12, 14]),
        (el, u'a1[2:4:2]', [12]),
        (el, u'a1[::-1]', [15, 14, 13, 12, 11, 10]),
        (el, u'a1[::-2]', [15, 13, 11]),
        (el, u'dt1', [today]),
        (el, u'dt1/year', [today.year]),
        (el, u'dt1/./year', [today.year]),
        ]
    for element, path, expected in _finders:
        yield _finds, element, path, expected


def test_find_strict_loose():
    el = Mixed.from_defaults()
    _cases = [
        (el, u'bogus'),
        (el, u'/d1/d1i3'),
        (el, u'l1[5]'),
        (el, u'l3[:]/missing'),
        ]

    for element, path in _cases:
        assert_raises(LookupError, element.find, path)

        found = element.find(path, strict=False)
        assert not found


def test_pathexpr():
    xy = pathexpr(u'x/y')
    assert xy is pathexpr(xy)
    assert xy == pathexpr([u'x', u'y'])


def _find_message(el, path, **find_kw):
    try:
        el.find(path, **find_kw)
    except LookupError as exc:
        return str(exc)
    assert False


def test_find_strict_messaging():
    el = Mixed.from_defaults()

    message = _find_message(el, u'bogus')
    expected = ("Unnamed element Mixed has no child u'bogus' "
                "in expression u'bogus'")
    assert expected in message

    message = _find_message(el, u'd1/bogus')
    expected = ("Dict element u'd1' has no child u'bogus' "
                "in expression u'd1/bogus'")
    assert expected in message

    message = _find_message(el, u'l1[5]')
    expected = ("List element u'l1' has no child u'5' "
                "in expression u'l1[5]'")
    assert expected in message


def test_find_default():
    el = Mixed.from_defaults()
    _cases = [
        (el, u'i1', [0]),
        (el, u'a1[:]', [10, 11, 12, 13, 14, 15]),
        (el, u'a1[0]', [10]),
        ]

    for element, path, expected in _cases:
        elements = element.find(path)
        found = [e.value for e in elements]
        assert found == expected


def test_find_single():
    el = Mixed.from_defaults()
    _cases = [
        (el, u'i1', 0),
        (el, u'bogus', None),
        (el, u'a1[0]', 10),
        (el, u'a1[10]', None),
        (el, u'l3[1:][1:]', 6),
        ]

    for element, path, expected in _cases:
        element = element.find(path, single=True, strict=False)
        if element is None:
            found = None
        else:
            found = element.value
        assert found == expected


def test_find_single_loose():
    el = Mixed.from_defaults()

    element = el.find(u'l3[:][:]', single=True, strict=False)
    found = element.value
    assert found == 6


def test_find_single_messaging():
    el = Mixed.from_defaults()

    message = _find_message(el, u'a1[:]', single=True)
    expected = "Path 'a1[:]' matched multiple elements; single result expected"
    assert expected in message
