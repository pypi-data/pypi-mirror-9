import itertools
import yter


def test_yany():
    assert yter.yany((0, 1, 2)) == 1
    assert yter.yany(itertools.chain(("a", 1, [2]))) == "a"
    assert yter.yany(iter(("", 0, []))) == []

    assert yter.yany((), empty=5) == 5
    assert yter.yany(iter(()), empty=5) == 5
    assert yter.yany((2,), empty=5) == 2

    assert yter.yany(("a", "aa", "aaa"), key=lambda x: len(x) - 1) == "aa"



def test_yall():
    assert yter.yall((0, 1, 2)) == 0
    assert yter.yall(itertools.chain(("a", 0, [2]))) == 0
    assert yter.yall(iter(("", 1, []))) == ""

    assert yter.yall((), empty=5) == 5
    assert yter.yall(iter(()), empty=5) == 5
    assert yter.yall((2,), empty=5) == 2

    assert yter.yall(("a", "aa", "aaa"), key=lambda x: len(x) - 1) == "a"


def test_last():
    assert yter.last((0, 1, 2)) == 2
    assert yter.last(itertools.chain((0, 1, 2))) == 2
    assert yter.last(iter(("", 1, []))) == []

    assert yter.last((), empty=5) == 5
    assert yter.last(iter(()), empty=5) == 5
    assert yter.last((2,), empty=5) == 2


def test_head():
    assert yter.head((0, 1, 2), 2) == [0, 1]
    assert yter.head((0, 1, 2), 5) == [0, 1, 2]
    assert yter.head(itertools.chain((0, 1, 2)), 1) == [0]
    assert yter.head(iter(("", 1, [])), 0) == []


def test_tail():
    assert yter.tail((0, 1, 2), 2) == [1, 2]
    assert yter.tail((0, 1, 2), 5) == [0, 1, 2]
    assert yter.tail(itertools.chain((0, 1, 2)), 1) == [2]
    assert yter.tail(iter(("", 1, [])), 0) == []


def test_finish():
    assert yter.finish((0, 1, 2)) == 3
    assert yter.finish(itertools.chain((0, 1, 2))) == 3
    assert yter.finish(iter(("", 1, []))) == 3
    y = iter("abc")
    assert yter.finish(y) == 3
    assert yter.finish(y) == 0

def test_minmax():
    assert yter.minmax((0, 1, 2)) == (0, 2)
    assert yter.minmax(iter((0, 2, 1))) == (0, 2)
    assert yter.minmax(itertools.chain((1, 2, 0))) == (0, 2)

    assert yter.minmax((), empty=5) == (5, 5)
    assert yter.minmax(iter(()), empty=5) == (5, 5)

    # Test stability, equal vals preserve order
    class e(object):
        def __lt__(self, other):
            return False
        def __ge__(self, other):
            return True
    e1 = e()
    e2 = e()
    e3 = e()
    assert yter.minmax((e1, e3, e2)) == (e1, e2)


def test_minmedmax():
    assert yter.minmedmax((0, 1, 2)) == (0, 1, 2)
    assert yter.minmedmax(iter((0, 2, 1))) == (0, 1, 2)
    assert yter.minmedmax(itertools.chain((1, 2, 0))) == (0, 1, 2)

    assert yter.minmedmax((), empty=5) == (5, 5, 5)
    assert yter.minmedmax(iter(()), empty=5) == (5, 5, 5)

    # Test stability, equal vals preserve order
    class e(object):
        def __lt__(self, other):
            return False
        def __ge__(self, other):
            return True
    e1 = e()
    e2 = e()
    e3 = e()
    assert yter.minmedmax((e1, e3, e2)) == (e1, e3, e2)


def test_isiter():
    assert yter.isiter((1,))
    assert yter.isiter({})
    assert yter.isiter([1])
    assert yter.isiter(range(1))

    assert not yter.isiter(None)
    assert not yter.isiter(9)
    assert not yter.isiter("")
    assert not yter.isiter("a")

    assert yter.isiter(itertools.chain((1,)))

