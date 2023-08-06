try:
    import ujson as json
except ImportError:
    import json

try:
    import jsonpath_rw
except ImportError:
    jsonpath_rw = None
try:
    import lxml.etree
except ImportError:
    lxml = None
try:
    import yaml
except ImportError:
    yaml = None


class QueryAttr(object):
    def __init__(self, query, factory=None):
        self.query = query
        self.factory = factory

    def __get__(self, obj, cls):
        if obj:
            return self.create(obj, obj.__document__.execute_query(self.query))
        else:
            return self

    def __call__(self, func):
        self.create = func
        return self

    def create(self, obj, value):
        if self.factory:
            return self.factory(value)
        else:
            return value


class CsvRow(object):
    class DocumentProxy(object):
        def __init__(self, row, header_map):
            self.row = row
            self.header_map = header_map

        def execute_query(self, column):
            if isinstance(column, int):
                return self.row[column]
            else:
                assert self.header_map
                return self.row[self.header_map[column]]

    def __init__(self, docproxy):
        self.__document__ = docproxy

    @classmethod
    def fromfile(cls, file, separator=",", read_header=False):
        if read_header:
            row = next(file)
            cols = row.strip().split(separator)
            header_map = {col: pos for pos, col in enumerate(cols)}
        else:
            header_map = None

        for row in file:
            yield cls(cls.DocumentProxy(row.rstrip().split(separator),
                                        header_map))


class XMLDoc(object):
    class DocumentProxy(object):
        @classmethod
        def create_parser(cls):
            return lxml.etree.XMLParser()

        def __init__(self, doc):
            self.doc = doc

        @classmethod
        def fromfile(cls, file):
            cls.assert_lxml()
            return cls(lxml.etree.parse(file, cls.create_parser()))

        @classmethod
        def fromstring(cls, str):
            cls.assert_lxml()
            return cls(lxml.etree.fromstring(str, cls.create_parser()))

        @classmethod
        def assert_lxml(cls):
            assert lxml, "'lxml' module required"

        def execute_query(self, xpath):
            # if xpath.startswith("//"):
            #     xpath = ".{}".format(xpath)
            nodes = self.doc.xpath(xpath)
            if nodes:
                return nodes[0]

        def set_iterables(self, query):
            self.iterables = iter(self.doc.xpath(query))

        def get_next_iterable(self):
            return next(self.iterables)

    def __init__(self, docproxy):
        self.__document__ = docproxy

    @classmethod
    def fromfile(cls, file):
        return cls(docproxy=cls.DocumentProxy.fromfile(file))

    @classmethod
    def fromstring(cls, str):
        return cls(docproxy=cls.DocumentProxy.fromstring(str))

    def __iter__(self):
        self.__document__.set_iterables(self.Iterable.__query__)
        return self

    def __next__(self):
        iterable = self.__document__.get_next_iterable()
        return self.Iterable(self.DocumentProxy(iterable))

    next = __next__  # Python 2 compatibility

    def __repr__(self):
        cls = self.__class__
        query_attributes = ["{}={!r}".format(attr, getattr(self, attr))
                            for attr in dir(cls)
                            if isinstance(getattr(cls, attr), QueryAttr)]
        return "<{class_name} ({query_attributes})>".format(
            class_name=cls.__name__,
            query_attributes=", ".join(query_attributes)
        )


class HTMLDoc(XMLDoc):
    class DocumentProxy(XMLDoc.DocumentProxy):
        @classmethod
        def create_parser(cls):
            return lxml.etree.HTMLParser()


class JSONDoc(XMLDoc):
    class DocumentProxy(object):
        def __init__(self, doc):
            self.doc = doc

        @classmethod
        def fromfile(cls, file):
            return cls(json.load(file))

        @classmethod
        def fromstring(cls, str):
            return cls(json.loads(str))

        def execute_query(self, json_path):
            assert jsonpath_rw, "'jsonpath_rw' module required"
            path_expr = jsonpath_rw.parse(json_path)
            values = [match.value for match in path_expr.find(self.doc)]
            if values:
                if len(values) > 1:
                    return values
                else:
                    return values[0]

        def set_iterables(self, query):
            self.iterables = iter(self.execute_query(query))

        def get_next_iterable(self):
            return next(self.iterables)


class YAMLDoc(JSONDoc):
    class DocumentProxy(JSONDoc.DocumentProxy):
        @classmethod
        def fromfile(cls, file):
            assert yaml, "'yaml' module required"
            return cls(yaml.load(file))

        @classmethod
        def fromstring(cls, string):
            return cls.fromfile(string)


def set_name(name):
    def decorator(decorated):
        decorated.__name__ = name
        return decorated
    return decorator
