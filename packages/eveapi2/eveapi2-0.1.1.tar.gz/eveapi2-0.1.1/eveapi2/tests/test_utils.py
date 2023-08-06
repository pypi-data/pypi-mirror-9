import pytest

from eveapi2.utils import xml_input


def test_xml_input():

    @xml_input
    def some_func(i):
        return i

    assert some_func('aa') == 'aa'

    with pytest.raises(TypeError):
        some_func(True)
