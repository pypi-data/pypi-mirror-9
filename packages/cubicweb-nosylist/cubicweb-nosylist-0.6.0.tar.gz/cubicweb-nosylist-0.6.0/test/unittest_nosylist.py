"""Nosy list unit tests"""

from cubicweb.devtools.testlib import CubicWebTC

class NosyListTestsCubicWebTC(CubicWebTC):
    """test nosylist specific behaviors"""

    def test_nosylist_added_after_adding_interested_in(self):
        with self.admin_access.repo_cnx() as cnx:
            user = self.create_user(cnx, 'test')
            cnx.execute('INSERT ObjectOfInterest O: O name "les fleurs"').get_entity(0, 0)
            rql = 'SET U interested_in O WHERE O name "les fleurs", U login "test"'
            cnx.execute(rql)
            rql = 'Any U WHERE O nosy_list U, O name "les fleurs", U login "test"'
            rset = cnx.execute(rql)
            self.assertEqual(len(rset), 1)
            self.assertEqual(rset[0][0], user.eid)

    def test_nosylist_propagation_creating_entity(self):
        with self.admin_access.repo_cnx() as cnx:
            usereid = self.create_user(cnx, 'test').eid
            cnx.commit()
        with self.new_access("test").repo_cnx() as cnx:
            cnx.execute('INSERT ObjectOfInterest O: O name "les gateaux"').get_entity(0, 0)
            rql = 'Any U WHERE O nosy_list U, O name "les gateaux"'
            rset = cnx.execute(rql)
            self.assertEqual(len(rset), 1)
            self.assertEqual(rset[0][0], usereid)

    def test_nosylist_deletion_after_interested_in_deletion(self):
        with self.admin_access.repo_cnx() as cnx:
            usereid = self.create_user(cnx, 'test')
            cnx.commit()
        with self.new_access("test").repo_cnx() as cnx:
            cnx.execute('INSERT ObjectOfInterest O: O name "les gateaux"').get_entity(0, 0)
            rql = 'Any U WHERE O nosy_list U, O name "les gateaux"'
            rset = cnx.execute(rql)
            rql = 'DELETE U interested_in O WHERE O name "les gateaux", U login "test"'
            cnx.execute(rql)
            rql = 'Any U WHERE O nosy_list U, O name "les gateaux"'
            rset = cnx.execute(rql)
            self.assertEqual(len(rset), 0)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
