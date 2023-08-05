import itertools
import yter


def test_call():
    assert tuple(yter.call((0, 1, lambda: 2))) == (0, 1, 2)
    assert tuple(yter.call(())) == ()


def test_percent():
    assert tuple(yter.percent((0, 1, 2), 0.5)) == (0, 2)

    numbers = tuple(range(100))
    assert tuple(yter.percent(numbers, 1)) == numbers
    assert tuple(yter.percent(numbers, 1.1)) == numbers
    assert tuple(yter.percent(numbers, 5.5)) == numbers

    assert len(tuple(yter.percent(numbers, 0))) == 0
    assert len(tuple(yter.percent(numbers, 0.0))) == 0
    assert len(tuple(yter.percent(numbers, 0.01))) == 1
    assert len(tuple(yter.percent(numbers, 0.11))) == 11
    assert len(tuple(yter.percent(numbers, .47))) == 47


def test_flat():
    assert tuple(yter.flat(((0, 1), (2,)))) == (0, 1, 2)


def test_chunk():
    assert tuple(map(tuple, yter.chunk((0, 1, 2), 2))) == ((0, 1), (2,))
    assert tuple(map(tuple, yter.chunk(itertools.chain((0, 1, 2)), 2))) == ((0, 1), (2,))

def test_key():
    assert tuple(yter.key(("one", "two", "three", "four"), len)) == (
        (3, "one"), (3, "two"), (5, "three"), (4, "four"))
