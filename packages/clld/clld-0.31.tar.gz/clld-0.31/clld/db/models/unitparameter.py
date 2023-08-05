from __future__ import unicode_literals, print_function, division, absolute_import

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from zope.interface import implementer

from clld.db.meta import Base, PolymorphicBaseMixin
from clld.db.versioned import Versioned
from clld import interfaces

from . import IdNameDescriptionMixin, DataMixin, HasDataMixin, FilesMixin, HasFilesMixin

__all__ = ('UnitDomainElement', 'UnitParameter')


class UnitDomainElement_data(Base, Versioned, DataMixin):
    pass


class UnitDomainElement_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IUnitDomainElement)
class UnitDomainElement(Base,
                        PolymorphicBaseMixin,
                        Versioned,
                        IdNameDescriptionMixin,
                        HasDataMixin,
                        HasFilesMixin):

    """Doamin element for the domain of a UnitParameter."""

    unitparameter_pk = Column(Integer, ForeignKey('unitparameter.pk'))
    ord = Column(Integer)

    # do we need a numeric value for these?


class UnitParameter_data(Base, Versioned, DataMixin):
    pass


class UnitParameter_files(Base, Versioned, FilesMixin):
    pass


@implementer(interfaces.IUnitParameter)
class UnitParameter(Base,
                    PolymorphicBaseMixin,
                    Versioned,
                    IdNameDescriptionMixin,
                    HasDataMixin,
                    HasFilesMixin):

    """A measurable attribute of a unit."""

    domain = relationship(
        'UnitDomainElement', backref='parameter', order_by=UnitDomainElement.id)
