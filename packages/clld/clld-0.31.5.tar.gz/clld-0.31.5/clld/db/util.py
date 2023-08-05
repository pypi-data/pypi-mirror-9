"""Database utilities."""
from __future__ import unicode_literals, print_function, division, absolute_import
import time
import re

from sqlalchemy import Integer, event
from sqlalchemy.orm import joinedload
from sqlalchemy.schema import DDL
from sqlalchemy.sql.expression import cast, func
import transaction

from clld.db.meta import DBSession, Base
from clld.db.models import common


def as_int(col):
    return cast(col, Integer)


def with_collkey_ddl():  # pragma: no cover
    """Register creation of collkey function.

    Can be called at module level in db initialization scripts to create the collkey
    function. Once a session is bound to an engine collkey can be used to create indexes
    or in order_by clauses, e.g.::

        Index('ducet', collkey(common.Value.name)).create(DBSession.bind)
    """
    event.listen(
        Base.metadata,
        'before_create',
        DDL("""
CREATE OR REPLACE FUNCTION collkey (text, text, bool, int4, bool) RETURNS bytea
    LANGUAGE 'c' IMMUTABLE STRICT AS
    '$libdir/collkey_icu.so',
    'pgsqlext_collkey';
""").execute_if(dialect='postgresql'))


class _CollKey(object):

    """Lazily check and cache collkey support in the database on first usage."""

    _query = "SELECT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'collkey')"

    @property
    def has_collkey(self):  # pragma: no cover
        result = DBSession.bind.dialect.name == 'postgresql'\
            and DBSession.scalar(self._query)
        self.__dict__['has_collkey'] = result  # cached overrides property
        return result

    def __call__(self, col, locale='root', special_at_4=True, level=4, numeric_sorting=False):
        """If supported by the database, we use pg_collkey for collation.

        The optional arguments are passed to the collkey function as described at
        http://pgxn.org/dist/pg_collkey/0.5.1/
        """
        if self.has_collkey:  # pragma: no cover
            return func.collkey(col, locale, special_at_4, level, numeric_sorting)
        return col


collkey = _CollKey()


def icontains(col, qs):
    """Infix search condition.

    Basic support is provided for specifying matches at beginning or end of the text.
    """
    spattern = re.compile('^(\^|\\\\b)')
    epattern = re.compile('(\$|\\\\b)$')

    prefix, suffix = '%', '%'
    if spattern.search(qs):
        qs = spattern.sub('', qs)
        prefix = ''

    if epattern.search(qs):
        qs = epattern.sub('', qs)
        suffix = ''

    return col.ilike(prefix + qs + suffix)


def compute_language_sources(*references):
    """compute relations between languages and sources.

    by going through the relevant models derived from the HasSource mixin.
    """
    old_sl = {}
    for pair in DBSession.query(common.LanguageSource):
        old_sl[(pair.source_pk, pair.language_pk)] = True

    references = list(references)
    references.extend([
        (common.ValueSetReference, 'valueset'),
        (common.SentenceReference, 'sentence')])
    sl = {}
    for model, attr in references:
        for ref in DBSession.query(model):
            sl[(ref.source_pk, getattr(ref, attr).language_pk)] = True

    for s, l in sl:
        if (s, l) not in old_sl:
            DBSession.add(common.LanguageSource(language_pk=l, source_pk=s))


def compute_number_of_values():
    """compute number of values per valueset and store it in valueset's jsondata."""
    for valueset in DBSession.query(common.ValueSet).options(
        joinedload(common.ValueSet.values)
    ):
        valueset.update_jsondata(_number_of_values=len(valueset.values))


def get_distinct_values(col, key=None):
    return sorted((c for c, in DBSession.query(col).distinct() if c), key=key)


def page_query(q, n=1000, verbose=False, commit=False):
    """Go through query results in batches.

    .. seealso:: http://stackoverflow.com/a/1217947
    """
    s = time.time()
    offset = 0
    while True:
        r = False
        for elem in q.limit(n).offset(offset):
            r = True
            yield elem
        if commit:  # pragma: no cover
            transaction.commit()
            transaction.begin()
        offset += n
        e = time.time()
        if verbose:
            print(e - s, offset, 'done')  # pragma: no cover
        s = e
        if not r:
            break
