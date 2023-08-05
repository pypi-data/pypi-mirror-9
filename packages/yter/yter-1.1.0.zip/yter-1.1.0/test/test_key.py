import pytest
import yter


def test_formatter():
    assert yter.formatter("val")(None) == "val"
    assert yter.formatter("{0:3d}")(22) == " 22"
    assert yter.formatter("{it}", it=True)(False) == "True"
    with pytest.raises(IndexError):
        yter.formatter("{1}")("one")



def test_numeric():
    assert yter.numeric("one2three") == ("one", 2, "three")
    assert yter.numeric("one-2three") == ("one", -2, "three")
    assert yter.numeric("1two3") == (1, "two", 3)
    assert yter.numeric("88") == (88,)
    assert yter.numeric("eight-eight") == ("eight-eight",)
    assert yter.numeric("eight-") == ("eight-",)
    assert yter.numeric("-") == ("-",)
    assert yter.numeric("") == ()

