from eveapi2.mixins import IterMixin, TagMixin


def test_iter_mixin():
    i = IterMixin()
    i.attr1 = 1
    i.attr2 = 2

    # dict internally calls __iter__ on the object.
    assert dict(i) == {'attr1': 1, 'attr2': 2}


def test_tag_mixin():
    tag = 'this is tag'
    t = TagMixin(tag)

    assert t._tag == tag
