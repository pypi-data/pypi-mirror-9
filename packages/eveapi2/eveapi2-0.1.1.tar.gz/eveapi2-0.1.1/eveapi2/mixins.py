class IterMixin:

    def __iter__(self):
        for k in dir(self):
            if not k.startswith('_'):
                yield (k, getattr(self, k))


class TagMixin:
    """
    Mixin class for adding tag init attribute.
    """

    def __init__(self, tag, *args, **kwargs):
        self._tag = tag
        super().__init__(*args, **kwargs)
