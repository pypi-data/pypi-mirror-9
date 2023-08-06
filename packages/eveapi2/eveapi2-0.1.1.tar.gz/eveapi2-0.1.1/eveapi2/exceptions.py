class APIError(Exception):
    code = None

    def __init__(self, tag):
        self._tag = tag
        self.code = int(tag['code'])
        super(APIError, self).__init__(self._tag.text)
