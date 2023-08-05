# -*- coding: utf-8 -*-
from .version import __version__,__authors__,__maintainer__,__email__,__url__,__license__


#############################################
#
# Don't import anything in __init__.py!
# Otherwise setup.py can't import the private constants above (__authors__, etc)
# because it won't have installed dependencies yet!
#
from .Quandl import (
    get,
    push,
    search,
    WrongFormat,
    MultisetLimit,
    ParsingError,
    CallLimitExceeded,
    DatasetNotFound,
    ErrorDownloading,
    MissingToken,
    DateNotRecognized,
    CodeFormatError
    )

###############################################