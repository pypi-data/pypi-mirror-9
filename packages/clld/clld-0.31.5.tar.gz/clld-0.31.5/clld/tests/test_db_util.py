from __future__ import unicode_literals

from clld.tests.util import TestWithDbAndData


class Tests(TestWithDbAndData):
    def test_compute_language_sources(self):
        from clld.db.util import compute_language_sources
        from clld.db.models.common import Source, Sentence, Language, SentenceReference
        from clld.db.meta import DBSession

        s = Sentence(id='sentenced', language=Language(id='newlang'))
        sr = SentenceReference(sentence=s, source=Source.first())
        DBSession.add(sr)
        DBSession.flush()
        compute_language_sources()

    def test_compute_number_of_values(self):
        from clld.db.util import compute_number_of_values
        compute_number_of_values()

    def test_icontains(self):
        from clld.db.util import icontains
        from clld.db.models.common import Dataset
        from clld.db.meta import DBSession

        for qs, count in [('Ata', 1), ('^ata$', 0), ('^data', 1), ('set$', 1)]:
            q = DBSession.query(Dataset).filter(icontains(Dataset.name, qs))
            self.assertEqual(q.count(), count)

    def test_collkey(self):
        from clld.db.util import collkey
        from clld.db.models.common import Language

        collkey(Language.name)
