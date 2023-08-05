from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import (
    IdNameDescriptionMixin,
    DataMixin, HasDataMixin, FilesMixin, HasFilesMixin,
    HasSourceMixin, Contributor)

__all__ = ('Contribution', 'ContributionReference', 'ContributionContributor')


class Contribution_data(Base, Versioned, DataMixin):
    pass


class Contribution_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IContribution)
class Contribution(Base,
                   PolymorphicBaseMixin,
                   Versioned,
                   IdNameDescriptionMixin,
                   HasDataMixin,
                   HasFilesMixin):

    """A set of data contributed within the same context by the same contributors."""

    __table_args__ = (UniqueConstraint('name'),)

    date = Column(Date)

    @property
    def primary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs,
                       key=lambda a: (a.ord, a.contributor.id)) if assoc.primary]

    @property
    def secondary_contributors(self):
        return [assoc.contributor for assoc in
                sorted(self.contributor_assocs,
                       key=lambda a: (a.ord, a.contributor.id)) if not assoc.primary]

    def formatted_contributors(self):
        contribs = [' and '.join(c.name for c in self.primary_contributors)]
        if self.secondary_contributors:
            contribs.append(' and '.join(c.name for c in self.secondary_contributors))
        return ' with '.join(contribs)


class ContributionReference(Base, Versioned, HasSourceMixin):

    """Association table."""

    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contribution = relationship(Contribution, backref="references")


class ContributionContributor(Base, PolymorphicBaseMixin, Versioned):

    """Many-to-many association between contributors and contributions."""

    contribution_pk = Column(Integer, ForeignKey('contribution.pk'))
    contributor_pk = Column(Integer, ForeignKey('contributor.pk'))

    # contributors are ordered.
    ord = Column(Integer, default=1)

    # we distinguish between primary and secondary (a.k.a. 'with ...') contributors.
    primary = Column(Boolean, default=True)

    contribution = relationship(Contribution, backref='contributor_assocs')
    contributor = relationship(Contributor, lazy=False, backref='contribution_assocs')
