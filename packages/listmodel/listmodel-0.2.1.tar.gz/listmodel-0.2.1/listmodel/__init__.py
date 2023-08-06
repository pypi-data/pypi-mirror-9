from pkg_resources import get_distribution

__author__ = "Jacques de Laval"
__project__ = "listmodel"
__version__ = get_distribution(__project__).version

from .models import (  # noqa
    CsvRow,
    JSONDoc,
    QueryAttr,
    set_name,
    TextDoc,
    XMLDoc,
    YAMLDoc
)
