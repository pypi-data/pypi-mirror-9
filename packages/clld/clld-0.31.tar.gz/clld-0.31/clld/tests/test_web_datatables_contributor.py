from clld.tests.util import TestWithEnv
from clld.db.models import common


class Tests(TestWithEnv):
    def test_Contributors(self):
        from clld.web.datatables.contributor import Contributors

        self.set_request_properties(params={
            'iSortingCols': '1',
            'iSortCol_0': '0',
            'sSortDir_0': 'desc'})

        self.handle_dt(Contributors, common.Contributor)
