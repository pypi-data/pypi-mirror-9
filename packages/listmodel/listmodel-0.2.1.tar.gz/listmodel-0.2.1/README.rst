Listmodel
=========
Listmodel is a Python library for object mappings for various list sources (XML documents, CSV documents, text documents, JSON/YAML objects) in a unified manner. Inspiration was taken from QML_ XmlListModel_.

.. _QML: http://en.wikipedia.org/wiki/QML
.. _XmlListModel: http://qt-project.org/doc/qt-4.8/qml-xmllistmodel.html

Basic usage
-----------
.. code-block:: python

    >>> from listmodel import XMLDoc, QueryAttr, set_name
    >>> xml = u"""<bookshelf>
    ...         <name>My Bookshelf</name>
    ...         <book>
    ...             <title>1984</title>
    ...             <author>Orwell, George</author>
    ...             <isbn>978-0-452-28423-4</isbn>
    ...             <chapter id="1">...</chapter>
    ...             <chapter id="2">...</chapter>
    ...             <chapter id="3">...</chapter>
    ...         </book>
    ...         <book>
    ...             <title>The man in the high castle</title>
    ...             <author>Dick, Philip K.</author>
    ...             <isbn>0679740678</isbn>
    ...             <chapter id="1">...</chapter>
    ...             <chapter id="2">...</chapter>
    ...             <chapter id="3">...</chapter>
    ...         </book>
    ...     </bookshelf>
    ... """
    >>> class Bookshelf(XMLDoc):
    ...     class Iterable(XMLDoc):
    ...         __query__ = "/bookshelf/book"
    ...
    ...         @set_name("Chapter")
    ...         class Iterable(XMLDoc):
    ...             __query__ = "chapter"
    ...             id = QueryAttr("@id")
    ...
    ...         isbn = QueryAttr("isbn/text()")
    ...         title = QueryAttr("title/text()")
    ...         author = QueryAttr("author/text()")
    ...
    ...         @QueryAttr("author/text()")
    ...         def author_first_name(self, value):
    ...             return value.split(", ")[1]
    ...
    ...     name = QueryAttr("/bookshelf/name/text()")
    >>> shelf = Bookshelf.fromstring(xml)
    >>> shelf
    <Bookshelf (name='My Bookshelf')>
    >>> shelf.name
    'My Bookshelf'
    >>> books = list(shelf)
    >>> len(books)
    2
    >>> books[1].title
    'The man in the high castle'
    >>> books[1].author_first_name
    'Philip K.'
    >>> list(books[0])
    [<Chapter (id='1')>, <Chapter (id='2')>, <Chapter (id='3')>]
