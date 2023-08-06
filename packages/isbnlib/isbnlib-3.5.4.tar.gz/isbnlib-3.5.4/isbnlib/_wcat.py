# -*- coding: utf-8 -*-
"""Query the worldcat.org xID service for metadata."""

import logging

from .dev import stdmeta
from .dev._exceptions import (DataWrongShapeError, NoDataForSelectorError,
                              RecordMappingError)
from .dev.bouth23 import u
from .dev.webquery import query as wquery

UA = 'isbnlib (gzip)'
SERVICE_URL = 'http://xisbn.worldcat.org/webservices/xid/isbn/{isbn}?'\
    'method=getMetadata&format=json&fl=title,author,year,publisher,lang'
LOGGER = logging.getLogger(__name__)


def _mapper(isbn, records):
    """Mapp: canonical <- records."""
    # canonical: ISBN-13, Title, Authors, Publisher, Year, Language
    try:
        canonical = {}
        canonical['ISBN-13'] = u(isbn)
        canonical['Title'] = records.get('title', u('')).replace(' :', ':')
        buf = records.get('author', u(''))
        canonical['Authors'] = [x.strip('. ') for x in buf.split(';')]
        canonical['Publisher'] = records.get('publisher', u(''))
        canonical['Year'] = records.get('year', u(''))
        canonical['Language'] = records.get('lang', u(''))
    except:  # pragma: no cover
        LOGGER.debug("RecordMappingError for %s with data %s", isbn, records)
        raise RecordMappingError(isbn)
    # call stdmeta for extra cleanning and validation
    return stdmeta(canonical)


def _records(isbn, data):
    """Classify (canonically) the parsed data."""
    try:
        # put the selected data in records
        recs = data['list'][0]
    except:  # pragma: no cover
        try:
            extra = data['stat']
            LOGGER.debug('DataWrongShapeError for %s with data %s',
                         isbn, extra)
        except:
            raise DataWrongShapeError(isbn)
        raise NoDataForSelectorError(isbn)

    # map canonical <- records
    return _mapper(isbn, recs)


def query(isbn):
    """Query the worldcat.org service for metadata."""
    data = wquery(SERVICE_URL.format(isbn=isbn), user_agent=UA)
    return _records(isbn, data)
