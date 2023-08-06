from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, String, Unicode, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from zope.interface import implementer
from six import iteritems

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces
from clld.lib import bibtex
from clld.lib import coins
from clld.web.util.htmllib import HTML

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    Language, LanguageSource)

__all__ = ('Source', 'HasSourceMixin')


class Source_data(Base, Versioned, DataMixin):
    pass


class Source_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.ISource)
class Source(Base,
             PolymorphicBaseMixin,
             Versioned,
             IdNameDescriptionMixin,
             HasDataMixin,
             HasFilesMixin):

    """A bibliographic record, cited as source for some statement."""

    glottolog_id = Column(String)
    google_book_search_id = Column(String)

    #
    # BibTeX fields:
    #
    bibtex_type = Column(bibtex.EntryType.db_type())
    author = Column(Unicode)
    year = Column(Unicode)
    title = Column(Unicode)
    type = Column(Unicode)
    booktitle = Column(Unicode)
    editor = Column(Unicode)
    pages = Column(Unicode)
    edition = Column(Unicode)
    journal = Column(Unicode)
    school = Column(Unicode)
    address = Column(Unicode)
    url = Column(Unicode)
    note = Column(Unicode)
    number = Column(Unicode)
    series = Column(Unicode)
    volume = Column(Unicode)
    publisher = Column(Unicode)
    organization = Column(Unicode)
    chapter = Column(Unicode)
    howpublished = Column(Unicode)

    # typed information we might want to use for searching or sorting:
    year_int = Column(Integer)
    startpage_int = Column(Integer)
    pages_int = Column(Integer)

    languages = relationship(
        Language, backref='sources', secondary=LanguageSource.__table__)

    @property
    def gbs_identifier(self):
        if not self.jsondata.get('gbs'):
            return
        if not self.jsondata['gbs']['volumeInfo'].get('industryIdentifiers'):
            return
        id_ = None
        for identifier in self.jsondata['gbs']['volumeInfo']['industryIdentifiers']:
            # prefer ISBN_13 over ISBN_10 over anything else
            if identifier['type'] == 'ISBN_13':
                id_ = 'ISBN:' + identifier['identifier']
            if identifier['type'] == 'ISBN_10' and not id_:
                id_ = 'ISBN:' + identifier['identifier']
        if not id_:
            # grab the last one in the list (most probably the only one!)
            id_ = identifier['identifier']
        return id_

    def __bibtex__(self):
        return {}

    def bibtex(self, exclude={'gbs', 'glottolog_ref_id'}):
        kw = {k: v for k, v in iteritems(self.jsondata) if k not in exclude}
        kw.update(self.__bibtex__())
        return bibtex.Record.from_object(self, **kw)

    def coins(self, req):
        return HTML.span(
            ' ',
            **coins.ContextObject.from_bibtex(
                req.dataset.name, self.bibtex()).span_attrs()
        )


#
# Several objects can be linked to sources, i.e. they can have references.
#
class HasSourceMixin(object):
    key = Column(Unicode)  # the citation key, specific (and unique) within a contribution
    description = Column(Unicode)  # e.g. page numbers.

    @declared_attr
    def source_pk(cls):
        return Column(Integer, ForeignKey('source.pk'))

    @declared_attr
    def source(cls):
        return relationship(Source, backref=cls.__name__.lower() + 's')
