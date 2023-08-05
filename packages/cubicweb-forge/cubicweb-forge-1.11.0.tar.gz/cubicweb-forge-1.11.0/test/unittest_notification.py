"""Forge hooks tests"""
import re

from cubicweb.devtools.testlib import MAILBOX
from cubes.tracker.testutils import TrackerBaseTC

class NotificationTC(TrackerBaseTC):

    def setUp(self):
        super(NotificationTC, self).setUp()
        # XXX should be done in devtools
        with self.admin_access.client_cnx() as cnx:
            rset = cnx.execute('INSERT EmailAddress E: E address "admin@cwo", U primary_email E '
                               'WHERE U login "admin"')
            self.assertTrue(rset)
            cnx.commit()

    def test_notifications(self):
        with self.admin_access.client_cnx() as cnx:
            p = self.create_project(cnx, 'hop').get_entity(0, 0)
            b = self.create_ticket(cnx, 'one more', pname='hop').get_entity(0, 0)
            cnx.execute('INSERT Comment X: X content "duh? explain", X comments B '
                        'WHERE B title "one more"')
            b.cw_set(priority=u'important')
            cnx.commit()
            MAILBOX.sort(key=lambda x:x.recipients)
            self.assertEqual(sorted(['[data] New Project: hop',
                                     '[data] New Project: hop', # see below
                                     '[hop] Ticket added: #EID one more',
                                     '[hop] new comment for Ticket #EID one more']),
                             sorted([re.sub('#\d+', '#EID', e.subject) for e in MAILBOX]))
            # test that for new project, recipients are the nosy list (eg creator)
            # *and* default recipients
            self.assertEqual(MAILBOX[0].recipients, ['admin@cwo'])
            self.assertEqual(MAILBOX[1].recipients, ['admin@cwo'])
            # but only nosy list for tickets / comments
            self.assertEqual(MAILBOX[2].recipients, ['admin@cwo'])
            self.assertEqual(MAILBOX[3].recipients, self.config['default-dest-addrs'])
            # check that other notification when project isn't being created are
            # using regulary nosy list recipients
            MAILBOX[:] = ()
            p.cw_adapt_to('IWorkflowable').fire_transition('temporarily stop development')
            cnx.commit()
            self.assertEqual([re.sub('#\d+', '#EID', e.subject) for e in MAILBOX],
                             ['[hop] project is now in state "asleep"',])
            self.assertEqual(MAILBOX[0].recipients, ['admin@cwo'])

    def test_nosy_list_propagation(self):
        with self.admin_access.client_cnx() as cnx:
            self.create_user(cnx, 'logilabien')
            cnx.execute('INSERT EmailAddress X: X address "logilabien@logilab.org", U primary_email X WHERE U login "logilabien"')
            cnx.execute('SET U interested_in X WHERE X name "cubicweb", U login "logilabien"')
            cnx.commit()
            ticket = self.create_ticket(cnx, 'ticket').get_entity(0, 0)
            cnx.commit()
            self.assertEqual(len(MAILBOX), 2)
            MAILBOX.sort(key=lambda x: x.recipients)
            self.assertEqual(MAILBOX[0].subject, '[cubicweb] Ticket added: #%s ticket' % ticket.eid)
            self.assertEqual(MAILBOX[0].recipients, ['admin@cwo'])
            self.assertEqual(MAILBOX[1].subject, '[cubicweb] Ticket added: #%s ticket' % ticket.eid)
            self.assertEqual(MAILBOX[1].recipients, ['logilabien@logilab.org'])


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
