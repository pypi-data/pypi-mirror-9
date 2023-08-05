"""functional tests for default forge security configuration"""
from cubicweb import Binary, Unauthorized
from cubicweb import devtools # necessary to import properly from cubes
from cubes.tracker.testutils import create_ticket_rql
from cubes.forge.testutils import ForgeSecurityTC

class ForgeSecurityTC(ForgeSecurityTC):

    def test_base_security(self):
        # staff users shouldn'- be able to insert/update project,extproject,license
        # but not "standard" users
        with self.new_access('staffuser').client_cnx() as cnx:
            # staff user insert
            cnx.execute('INSERT ExtProject X: X name "myprojet"')
            cnx.commit() # OK
            cnx.execute('INSERT License X: X name "mylicense"')
            self.assertRaises(Unauthorized, cnx.commit)
            # staff user update projects he doesn't own
            try:
                cnx.execute('SET X name "mycubicweb" WHERE X is ExtProject, X name "projet externe"')
                cnx.commit() # OK
            finally: # manual rollback
                cnx.execute('SET X name "projet externe" WHERE X is ExtProject, X name "mycubicweb"')
                cnx.commit() # OK
            cnx.execute('SET X name "license1" WHERE X is License, X name "license"')
            self.assertRaises(Unauthorized, cnx.commit)

        with self.new_access('stduser').client_cnx() as cnx:
            # standard user create
            cnx.execute('INSERT ExtProject X: X name "mystdprojet"')
            self.assertRaises(Unauthorized, cnx.commit)
            cnx.execute('INSERT License X: X name "mystdlicense"')
            self.assertRaises(Unauthorized, cnx.commit)
            cnx.rollback()
            # licenses are public
            self.assertGreaterEqual(len(cnx.execute('Any X WHERE X is License')), 1)
            # standard user try to update
            cnx.execute('SET X name "projet externe renamed" WHERE X is ExtProject, X name "projet externe"')
            self.assertRaises(Unauthorized, cnx.commit)
            cnx.execute('SET X name "license renamed" WHERE X is License, X name "license"')
            self.assertRaises(Unauthorized, cnx.commit)

    def _test_ticket_with_cubicweb_local_role(self, cnx):
        # cubicweb client/developper user attach something to a ticket
        ticket = cnx.execute(*create_ticket_rql('a ticket', 'cubicweb')).get_entity(0, 0)
        cnx.commit() # OK
        # and add file or image attachment
        cnx.execute('INSERT File X: X data %(data)s, X data_name %(name)s, T attachment X WHERE T eid %(t)s',
                   {'data': Binary('hop'), 'name': u'hop.txt', 't': ticket.eid})
        cnx.commit() # OK
        cnx.execute('INSERT File X: X data %(data)s, X data_name %(name)s, T attachment X WHERE T eid %(t)s',
                   {'data': Binary('hop'), 'name': u'hop.png', 't': ticket.eid})
        cnx.commit() # OK
        self.assertEqual(len(ticket.attachment), 2)

    def test_ticket_developper_security(self):
        # cubicweb developer user submit ticket
        with self.new_access('prj1developer').client_cnx() as cnx:
            self._test_ticket_with_cubicweb_local_role(cnx)

    def test_ticket_client_security(self):
        # cubicweb client user submit ticket
        with self.new_access('prj1client').client_cnx() as cnx:
            self._test_ticket_with_cubicweb_local_role(cnx)


    def test_ticket_workflow(self):
        with self.admin_access.client_cnx() as cnx:
            b = self.create_ticket(cnx, 'a ticket').get_entity(0, 0)
            cnx.commit() # to set initial state properly
            self.assertEqual(b.cw_adapt_to('IWorkflowable').state, 'open')
            beid = b.eid

        # only project's developer or user in the staff group can pass the wait for feedback transition
        self._test_tr_fail('stduser', beid, 'wait for feedback')
        self._test_tr_fail('prj1client', beid, 'wait for feedback')
        self._test_tr_success('prj1developer', beid, 'wait for feedback')
        # project's client, developer or user in the staff group can pass the
        # got feedback transition. Got feedback is a 'go back' transition
        self._test_tr_fail('stduser', beid, 'got feedback')
        self._test_tr_success('prj1client', beid, 'got feedback')
        #self._test_tr_success('staffuser', beid, 'got feedback')

        with self.admin_access.client_cnx() as cnx:
            b = cnx.entity_from_eid(beid)
            self.assertEqual(b.cw_adapt_to('IWorkflowable').state, 'open')

        # only staff/developer can pass the start transition
        self._test_tr_fail('stduser', beid, 'start')
        self._test_tr_fail('prj1client', beid, 'start')
        self._test_tr_success('prj1developer', beid, 'start')
        #self._test_tr_success('staffuser', beid, 'start')
        # project's client, developer or user in the staff group can pass the
        # got feedback transition. Got feedback is a 'go back' transition
        self._test_tr_success('staffuser', beid, 'wait for feedback')
        self._test_tr_success('prj1developer', beid, 'got feedback')

        with self.admin_access.client_cnx() as cnx:
            b = cnx.entity_from_eid(beid)
            self.assertEqual(b.cw_adapt_to('IWorkflowable').state, 'in-progress')

        # staff/cubicweb developer can modify tickets even once no more in the open state
        with self.new_access('staffuser').client_cnx() as cnx:
            cnx.execute('SET X description "bla" WHERE X eid %(x)s', {'x': beid})
            cnx.commit() # OK

        with self.new_access('prj1developer').client_cnx() as cnx:
            cnx.execute('SET X description "bla bla" WHERE X eid %(x)s', {'x': beid})
            cnx.commit() # OK

        # though client can't, even their own tickets
        with self.new_access('prj1client').client_cnx() as cnx:
            cnx.execute('SET X description "bla bla bla" WHERE X eid %(x)s', {'x': beid})
            self.assertRaises(Unauthorized, cnx.commit)
            tceid = cnx.execute(*create_ticket_rql('a ticket', 'cubicweb'))[0][0]
            cnx.commit() # ok

        self._test_tr_success('staffuser', tceid, 'start')

        with self.new_access('prj1client').client_cnx() as cnx:
            cnx.execute('SET X description "bla" WHERE X eid %(x)s', {'x': tceid})
            self.assertRaises(Unauthorized, cnx.commit)

        # only staff/developer can pass the done transition
        self._test_tr_fail('stduser', beid, 'done')
        self._test_tr_fail('prj1client', beid, 'done')
        self._test_tr_success('prj1developer', beid, 'done')
        # only staff/developer can pass the done transition XXX actually done automatically on version publishing
        self._test_tr_fail('stduser', beid, 'ask validation')
        self._test_tr_fail('prj1client', beid, 'ask validation')
        self._test_tr_success('prj1developer', beid, 'ask validation')
        #self._test_tr_success('staffuser', beid, 'done')
        # only staff/client can pass the resolve transition (though clients should,
        # use jplextranet for that
        self._test_tr_fail('prj1developer', beid, 'resolve')
        self._test_tr_success('prj1client', beid, 'resolve')
        #self._test_tr_success('staffuser', beid, 'resolve')
        # managers can do what they want, even going to a state without existing transition...
        with self.admin_access.client_cnx() as cnx:
            b = cnx.entity_from_eid(beid)
            b.cw_adapt_to('IWorkflowable').change_state('validation pending')
            cnx.commit()

        # only staff/client can pass the reopen transition
        self._test_tr_fail('stduser', beid, 'refuse validation')
        self._test_tr_fail('prj1developer', beid, 'refuse validation')
        self._test_tr_success('prj1client', beid, 'refuse validation')
        with self.admin_access.client_cnx() as cnx:
            b = cnx.entity_from_eid(beid)
            b.cw_adapt_to('IWorkflowable').change_state('open')
            cnx.commit()
        # only staff/developer can pass the reject transition
        self._test_tr_fail('prj1client', beid, 'reject')
        self._test_tr_success('prj1developer', beid, 'reject')
        # staff/developer/client can pass the deprecate transition
        with self.admin_access.client_cnx() as cnx:
            b = cnx.entity_from_eid(beid)
            b.cw_adapt_to('IWorkflowable').change_state('open')
            cnx.commit()
        self._test_tr_fail('stduser', beid, 'deprecate')
        self._test_tr_success('prj1developer', beid, 'deprecate')
        with self.admin_access.client_cnx() as cnx:
            b = cnx.entity_from_eid(beid)
            b.cw_adapt_to('IWorkflowable').change_state('open')
            cnx.commit()
        self._test_tr_success('prj1client', beid, 'deprecate')

    def test_version_security(self):
        # cubicweb client add a version
        with self.new_access('prj1client').client_cnx() as cnx:
            self.create_version(cnx, '3.6')
            cnx.commit()

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
