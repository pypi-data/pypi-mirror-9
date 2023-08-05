"""Forge unit tests"""
from __future__ import with_statement

from datetime import datetime, timedelta

from PIL import Image

from logilab.common.testlib import unittest_main, SkipTest

from cubicweb.devtools import ApptestConfiguration, PostgresApptestConfiguration
from cubicweb.devtools.testlib import AutoPopulateTest

from cubicweb import ValidationError, Unauthorized, Binary
from cubicweb import NoSelectableObject
from cubicweb.web.views import actions, workflow, idownloadable

from cubes.tracker.testutils import TrackerBaseTC
from cubes.forge.testutils import MyValueGenerator

from cubes.tracker.views import ticket, document
from cubes.comment import views as commentactions
from cubes.forge.views import project as myproject, boxes
from cubes.nosylist import views as nosylist

ONEDAY = timedelta(1)


class ForgeTests(TrackerBaseTC):
    """test forge specific behaviours"""

    def test_schema(self):
        seealso = self.schema['see_also']
        self.assert_('Ticket' in seealso.subjects(), seealso.subjects())

class ProjectTC(TrackerBaseTC):
    """Project"""

    def test_followup_wf(self):
        with self.admin_access.client_cnx() as cnx:
            ticket = cnx.execute('INSERT Ticket X: X title "parent", X concerns P, X load 1 '
                                  'WHERE P is Project').get_entity(0, 0)
            cnx.commit()
            iworkflowable = ticket.cw_adapt_to('IWorkflowable')
            for tr, state in [('done', 'done'),
                              ('ask validation', 'validation pending'),
                              ('refuse validation', 'not validated')]:
                iworkflowable.fire_transition(tr)
                cnx.commit()
                ticket.cw_clear_all_caches()
                self.assertEqual(iworkflowable.state, state)

    def test_download_box(self):
        with self.admin_access.web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertRaises(NoSelectableObject,
                              self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
            req.execute('SET X downloadurl "ftp://ftp.logilab.org/pub/cubicweb/" WHERE X is Project')
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertRaises(NoSelectableObject,
                              self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
            v = self.create_version(req, '0.0.0').get_entity(0, 0)
            req.cnx.commit()
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertRaises(NoSelectableObject,
                              self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
            v.cw_adapt_to('IWorkflowable').change_state('published')
            req.cnx.commit()
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                                  boxes.ProjectDownloadBox)
            req.cnx.commit()

        with self.new_access('anon').web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                                  boxes.ProjectDownloadBox)

    def test_possible_actions(self):
        with self.admin_access.web_request() as req:
            # manager user, in dev project
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertCountEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('managepermission', actions.ManagePermissionsAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('delete', actions.DeleteAction),
                                  ('copy', actions.CopyAction),
                                  ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                                  ('addticket', myproject.ProjectAddTicket),
                                  ('addversion', myproject.ProjectAddVersion),
                                  ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                                  ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                                  ('addscreenshot', myproject.ProjectAddScreenshot),
                                  ('addtestcard', myproject.ProjectAddTestCard),
                                  ('addsubproject', myproject.ProjectAddSubProject),
                                  ('pvrestexport', document.ProjectVersionExportAction),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                  [])
            proj = req.entity_from_eid(self.cubicweb)
            wf = proj.cw_adapt_to('IWorkflowable').current_workflow
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'temporarily stop development', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                                   wf.transition_by_name('temporarily stop development').eid),
                                  (u'stop maintainance', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                                   wf.transition_by_name('stop maintainance').eid),
                                  (u'project moved', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                                   wf.transition_by_name('project moved').eid),
                                  (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)
                                   ])
            # logilab user
            self.create_user(req, 'logilabien', ('staff', 'users'))
            req.cnx.commit()

        with self.new_access('logilabien').web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('copy', actions.CopyAction),
                                  ('addticket', myproject.ProjectAddTicket),
                                  ('addversion', myproject.ProjectAddVersion),
                                  ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                                  ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                                  ('addscreenshot', myproject.ProjectAddScreenshot),
                                  ('addtestcard', myproject.ProjectAddTestCard),
                                  ('addsubproject', myproject.ProjectAddSubProject),
                                  ('pvrestexport', document.ProjectVersionExportAction),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            proj = req.entity_from_eid(self.cubicweb)
            wf = proj.cw_adapt_to('IWorkflowable').current_workflow
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'temporarily stop development', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                                   wf.transition_by_name('temporarily stop development').eid),
                                  (u'stop maintainance', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                                   wf.transition_by_name('stop maintainance').eid),
                                  (u'project moved', u'http://testing.fr/cubicweb/project/cubicweb?treid=%s&vid=statuschange' %
                                   wf.transition_by_name('project moved').eid),
                                  (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)
                                  ])
        # guest user
        with self.new_access('anon').web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('pvrestexport', document.ProjectVersionExportAction),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [])

        with self.admin_access.client_cnx() as cnx:
            self.create_user(cnx, 'toto')
            cnx.commit()
        # std user, in dev project
        with self.new_access('toto').web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('pvrestexport', document.ProjectVersionExportAction),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [])

        with self.admin_access.client_cnx() as cnx:
            self.grant_permission(cnx, self.cubicweb, 'users', 'developer',
                                  'soumettre sur cubicweb')
            cnx.commit()
        # std user with perm, in dev project
        with self.new_access('toto').web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('addticket', myproject.ProjectAddTicket),
                                  ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                                  ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                                  ('addscreenshot', myproject.ProjectAddScreenshot),
                                  ('addtestcard', myproject.ProjectAddTestCard),
                                  ('pvrestexport', document.ProjectVersionExportAction),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [])
        with self.admin_access.client_cnx() as cnx:
            self.grant_permission(cnx, self.cubicweb, 'users', 'client',
                                  'nouvelle version')
            cnx.commit()
        # std user with client perm, in dev project
        with self.new_access('toto').web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('addticket', myproject.ProjectAddTicket),
                                  ('addversion', myproject.ProjectAddVersion),
                                  ('adddocumentationcard', myproject.ProjectAddDocumentationCard),
                                  ('adddocumentationfile', myproject.ProjectAddDocumentationFile),
                                  ('addscreenshot', myproject.ProjectAddScreenshot),
                                  ('addtestcard', myproject.ProjectAddTestCard),
                                  ('pvrestexport', document.ProjectVersionExportAction),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [])
        # manager user, moved project
        with self.admin_access.client_cnx() as cnx:
            proj = cnx.entity_from_eid(self.cubicweb)
            proj.cw_adapt_to('IWorkflowable').fire_transition('project moved')
            cnx.commit()
        with self.admin_access.web_request() as req:
            rset = req.execute('Any X WHERE X is Project, X name "cubicweb"')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('managepermission', actions.ManagePermissionsAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('delete', actions.DeleteAction),
                                  ('copy', actions.CopyAction),
                                  ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                                  ('pvrestexport', document.ProjectVersionExportAction),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'view history', u'http://testing.fr/cubicweb/project/cubicweb?vid=wfhistory')])

    def test_doap(self):
        with self.admin_access.web_request() as req:
            self.create_version(req, '0.1.0')
            req.execute('INSERT MailingList M: M name "python-projects", '
                        'M email_address "python-projects@logilab.org", M mailinglist_of P '
                        'WHERE P is Project')[0]
            proj = req.entity_from_eid(self.cubicweb)
            proj.view('doap')

    def test_creator_interested_in(self):
        with self.admin_access.client_cnx() as cnx:
            proj = cnx.entity_from_eid(self.cubicweb)
            self.assertEqual(len(proj.reverse_interested_in), 1)

    def test_add_icon(self):
        """ Add an icon to the project, check its new size and format. """
        # add an icon `tux.png` of size 200 x 232
        img = Binary.from_file(self.datapath('tux.png'))
        with self.admin_access.client_cnx() as cnx:
            proj = cnx.entity_from_eid(self.cubicweb)
            proj.cw_set(icon=img)
            cnx.commit()
            proj.cw_clear_all_caches()
            # read the icon image, check its size and format
            icon = Image.open(proj.icon)
            self.assertEqual(50, max(icon.size))
            self.assertEqual('image/png', proj.icon_format)

    def test_add_bad_icon(self):
        """ Add an invalid icon to the project, check ValueError is raised."""
        # add garbage
        img = Binary("I don't exist")
        with self.admin_access.client_cnx() as cnx:
            proj = cnx.entity_from_eid(self.cubicweb)
            with self.assertRaises(ValueError):
                proj.cw_set(icon=img)
            self.assertEqual(None, proj.icon_format)


class VersionTC(TrackerBaseTC):
    """Version"""
    def setup_database(self):
        super(VersionTC, self).setup_database()
        with self.admin_access.repo_cnx() as cnx:
            self.v = self.create_version(cnx, u'0.0.0')[0][0]
            cnx.commit()

    def test_download_box(self):
        with self.admin_access.web_request() as req:
            rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
            self.assertRaises(NoSelectableObject,
                              self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
            req.execute('SET X downloadurl "ftp://ftp.logilab.org/pub/cubicweb/" WHERE X is Project')
            rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
            self.assertRaises(NoSelectableObject,
                              self.vreg['ctxcomponents'].select, 'download_box', req, rset=rset)
            v = req.entity_from_eid(self.v)
            v.cw_adapt_to('IWorkflowable').change_state('published')
            req.cnx.commit()
            rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
            self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                                  idownloadable.DownloadBox)
            req.cnx.commit()

        with self.new_access('anon').web_request() as req:
            rset = req.execute('Any X WHERE X is Version, X num "0.0.0"')
            self.assertIsInstance(self.vreg['ctxcomponents'].select('download_box', req, rset=rset),
                                  idownloadable.DownloadBox)

class TicketTC(TrackerBaseTC):
    """Ticket"""

    def setup_database(self):
        super(TicketTC, self).setup_database()
        with self.admin_access.client_cnx() as cnx:
            self.v = self.create_version(cnx, u'0.0.0')[0][0]
            self.t1 = self.create_ticket(cnx, u"story1")[0][0]
            cnx.commit()

    def test_creator_interested_in(self):
        with self.admin_access.client_cnx() as cnx:
            t = self.create_ticket(cnx, 'pouet').get_entity(0, 0)
            self.assertEqual(len(t.reverse_interested_in), 1)

    def test_load_after_state_changed_deprecated(self):
        with self.admin_access.client_cnx() as cnx:
            t1 = cnx.entity_from_eid(self.t1)
            t1.cw_set(load=2)
            t1.cw_adapt_to('IWorkflowable').change_state('deprecated')
            cnx.commit()
            t1.cw_attr_cache.pop('load', None)
            self.assertEqual(t1.load, 0)

    def test_load_after_state_changed_rejected(self):
        with self.admin_access.client_cnx() as cnx:
            t1 = cnx.entity_from_eid(self.t1)
            t1.cw_set(load=2)
            t1.cw_adapt_to('IWorkflowable').change_state('rejected')
            cnx.commit()
            t1.cw_attr_cache.pop('load', None)
            self.assertEqual(t1.load, 0)

    def test_auto_set_load_left_1(self):
        with self.admin_access.client_cnx() as cnx:
            t = cnx.execute('INSERT Ticket X: X title "story1", X concerns P, X load 1 '
                             'WHERE P is Project').get_entity(0, 0)
            self.assertEqual(t.load_left, 1.0)

    def test_auto_set_load_left_2(self):
        with self.admin_access.client_cnx() as cnx:
            t1 = cnx.entity_from_eid(self.t1)
            cnx.execute('SET X load 1 WHERE X eid %(x)s', {'x': self.t1})
            t1.cw_attr_cache.pop('load_left', None)
            self.assertEqual(t1.load_left, 1)
            cnx.execute('SET X load 2 WHERE X eid %(x)s', {'x': self.t1})
            t1.cw_attr_cache.pop('load_left', None)
            self.assertEqual(t1.load_left, 1)

    def test_modification_date_after_comment_added(self):
        olddate = datetime.today() - ONEDAY
        with self.admin_access.client_cnx() as cnx:
            t1 = cnx.entity_from_eid(self.t1)
            t1.cw_set(modification_date=olddate)
            ceid = cnx.execute('INSERT Comment C: C content "A commment", C comments X '
                               'WHERE X eid %(x)s', {'x': self.t1})[0][0]
            cnx.commit()
            self.assertModificationDateGreater(t1, olddate)
            t1.cw_set(modification_date=olddate)
            ceid2 = cnx.execute('INSERT Comment C: C content "A commment", C comments X '
                                'WHERE X eid %(x)s', {'x': ceid})[0][0]
            cnx.commit()
            self.assertModificationDateGreater(t1, olddate)
            t1.cw_set(modification_date=olddate)
            cnx.execute('INSERT Comment C: C content "A commment", C comments X '
                        'WHERE X eid %(x)s', {'x': ceid2})
            cnx.commit()
            self.assertModificationDateGreater(t1, olddate)

    def test_modification_date_not_changed_if_not_ticket(self):
        # Commentable entities other than tickets should not have their
        # modification_date updated upon comments. Card is one of these.
        # Regression test for ticket #2961589.
        with self.admin_access.client_cnx() as cnx:
            card = cnx.execute('INSERT Card X: X title "Manaul", P documented_by X'
                               '   WHERE P is Project').get_entity(0, 0)
            olddate = datetime.today() - ONEDAY
            card.cw_set(modification_date=olddate)
            cnx.execute('INSERT Comment C: C content "Typo included", '
                         '  C comments X WHERE X eid %(x)s', {'x': card.eid})
            cnx.commit()
            card.cw_attr_cache.pop('modification_date', None)
            self.assertEqual(olddate, card.modification_date)

    def test_possible_actions(self):
        with self.admin_access.web_request() as req:
            rset = req.execute('Any X WHERE X is Ticket')
            _ticket = rset.get_entity(0, 0)
            teid = rset[0][0]
            self.assertCountEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('managepermission', actions.ManagePermissionsAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('delete', actions.DeleteAction),
                                  ('copy', actions.CopyAction),
                                  ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                                  ('movetonext', ticket.TicketMoveToNextVersionActions),
                                  ('reply_comment', commentactions.AddCommentAction)])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                  [('add Ticket attachment File subject',
                                    'http://testing.fr/cubicweb/add/File?__linkto=attachment%%3A%s%%3Aobject&__redirectpath=ticket%%2F%s&__redirectvid='
                                    % (teid, teid)),
                                   ('add Card test_case_for Ticket object',
                                    'http://testing.fr/cubicweb/add/Card?__linkto=test_case_for%%3A%s%%3Asubject&__redirectpath=ticket%%2F%s&__redirectvid='
                                    % (teid, teid))])
            t1 = req.entity_from_eid(self.t1)
            wf = t1.cw_adapt_to('IWorkflowable').current_workflow
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'start', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('start').eid)),
                                  (u'reject', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('reject').eid)),
                                  (u'done', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('done').eid)),
                                  (u'deprecate', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('deprecate').eid)),
                                  (u'wait for feedback', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('wait for feedback').eid)),
                                  (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid)])
            movetonext = self.action_submenu(req, rset, 'movetonext')
            self.assertEqual(len(movetonext), 1)
            self.assertEqual(movetonext[0][0], '0.0.0')
        anon_access = self.new_access('anon')
        with anon_access.web_request() as req:
            rset = req.execute('Any X WHERE X is Ticket')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('addrelated', actions.AddRelatedActions),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [])
        with self.admin_access.web_request() as req:
            t1 = req.entity_from_eid(self.t1)
            t1.cw_adapt_to('IWorkflowable').fire_transition('done')
            req.cnx.commit()
            rset = req.execute('Any X WHERE X is Ticket')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('managepermission', actions.ManagePermissionsAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('delete', actions.DeleteAction),
                                  ('copy', actions.CopyAction),
                                  ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                                  ('reply_comment', commentactions.AddCommentAction)])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                  [('add Ticket attachment File subject',
                                    'http://testing.fr/cubicweb/add/File?__linkto=attachment%%3A%s%%3Aobject&__redirectpath=ticket%%2F%s&__redirectvid='
                                    % (teid, teid)),
                                   ('add Card test_case_for Ticket object',
                                    'http://testing.fr/cubicweb/add/Card?__linkto=test_case_for%%3A%s%%3Asubject&__redirectpath=ticket%%2F%s&__redirectvid='
                                    % (teid, teid))])
            wf = t1.cw_adapt_to('IWorkflowable').current_workflow
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'ask validation', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('ask validation').eid)),
                                  (u'reopen', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('reopen').eid)),
                                  (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid),
                                  (u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1)])

        with anon_access.web_request() as req:
            rset = req.execute('Any X WHERE X is Ticket')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('addrelated', actions.AddRelatedActions),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1)])

        with self.admin_access.web_request() as req:
            t1 = req.entity_from_eid(self.t1)
            t1.cw_adapt_to('IWorkflowable').fire_transition('ask validation')
            req.cnx.commit()
            rset = req.execute('Any X WHERE X is Ticket')
            wf = t1.cw_adapt_to('IWorkflowable').current_workflow
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'resolve', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('resolve').eid)),
                                  (u'refuse validation', u'http://testing.fr/cubicweb/ticket/%s?treid=%s&vid=statuschange' %
                                   (self.t1, wf.transition_by_name('refuse validation').eid)),
                                  (u'view workflow', u'http://testing.fr/cubicweb/workflow/%s'  % wf.eid),
                                  (u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1)])
            t1.cw_adapt_to('IWorkflowable').fire_transition('resolve')
            req.cnx.commit()
            rset = req.execute('Any X WHERE X is Ticket')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('edit', actions.ModifyAction),
                                  ('managepermission', actions.ManagePermissionsAction),
                                  ('addrelated', actions.AddRelatedActions),
                                  ('delete', actions.DeleteAction),
                                  ('copy', actions.CopyAction),
                                  ('actionsbox_notifications_mgmt', nosylist.INosyListManageNotificationsAction),
                                  ('reply_comment', commentactions.AddCommentAction)])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [('add Ticket attachment File subject',
                                   'http://testing.fr/cubicweb/add/File?__linkto=attachment%%3A%s%%3Aobject&__redirectpath=ticket%%2F%s&__redirectvid='
                                   % (teid, teid)),
                                  ('add Card test_case_for Ticket object',
                                   'http://testing.fr/cubicweb/add/Card?__linkto=test_case_for%%3A%s%%3Asubject&__redirectpath=ticket%%2F%s&__redirectvid='
                                   % (teid, teid))])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1)])

        with anon_access.web_request() as req:
            rset = req.execute('Any X WHERE X is Ticket')
            self.assertListEqual(self.pactions(req, rset),
                                 [('workflow', workflow.WorkflowActions),
                                  ('addrelated', actions.AddRelatedActions),
                                  ])
            self.assertListEqual(self.action_submenu(req, rset, 'addrelated'),
                                 [])
            self.assertListEqual(self.action_submenu(req, rset, 'workflow'),
                                 [(u'view history', u'http://testing.fr/cubicweb/ticket/%s?vid=wfhistory' % self.t1)])

    def test_state_change_on_version_publishing(self):
        with self.admin_access.client_cnx() as cnx:
            v2 = cnx.execute('INSERT Version V: V num "0.0.1", V version_of P '
                              'WHERE P is Project').get_entity(0, 0)
            t1 = cnx.entity_from_eid(self.t1)
            t1.cw_set(done_in=v2)
            cnx.commit()
            t1iwf = t1.cw_adapt_to('IWorkflowable')
            t1iwf.fire_transition('done')
            t1.cw_clear_all_caches()
            self.assertEqual(t1iwf.state, 'done')
            cnx.commit()
            v2iwf = v2.cw_adapt_to('IWorkflowable')
            self.assertEqual(v2iwf.state, 'dev')
            v2.cw_clear_all_caches()
            v2iwf.change_state('published')
            cnx.commit()
            t1.cw_clear_all_caches()
            self.assertEqual(t1iwf.state, 'validation pending')

    def test_version_publishing_cant_change_ticket_state(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute('INSERT CWGroup X: X name "cubicwebdevelopers"')
            self.grant_permission(cnx, self.cubicweb, 'cubicwebdevelopers',
                                  u'developer')
            self.create_user(cnx, 'prj1client', groups=('users', 'cubicwebdevelopers'))
            cnx.commit()
            t1 = cnx.entity_from_eid(self.t1)
            t1.cw_set(done_in=self.v)
            # -  change ticket status
            t1iwf= t1.cw_adapt_to('IWorkflowable')
            t1iwf.fire_transition('done')
            t1.cw_clear_all_caches()
            self.assertEqual(t1iwf.state, 'done')
            # -  Remove permission on the ticket for the clients
            cnx.execute('DELETE X require_permission P WHERE X eid %s' % self.t1)
            cnx.commit()
        # - publish version as client
        with self.new_access('prj1client').client_cnx() as cnx:
            v2 = cnx.execute('Any X WHERE X version_of P, P name "cubicweb", P is Project, X num "0.0.0"').get_entity(0, 0)
            t1 = cnx.execute('Any X WHERE X in_state S, S name SN, X eid %s'% self.t1).get_entity(0, 0)
            # - can't change ticket's state
            t1iwf= t1.cw_adapt_to('IWorkflowable')
            self.assertRaises(ValidationError, t1iwf.fire_transition, 'ask validation')
            cnx.rollback()
            v2.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # - verify that ticket on which permissions were revoked remains in state
            self.assertEqual(t1iwf.state, 'done')
            # only managers are enabled to move away ticket from a published version
            self.assertRaises(Unauthorized, cnx.execute,
                              'DELETE X done_in V WHERE X eid %(x)s', {'x': self.t1})
            cnx.rollback()

        with self.admin_access.client_cnx() as cnx:
            self.create_user(cnx, 'staffuser', groups=('users', 'staff',))
            cnx.commit()

        with self.new_access('staffuser').client_cnx() as cnx:
            self.assertRaises(Unauthorized, cnx.execute,
                              'DELETE X done_in V WHERE X eid %(x)s', {'x': self.t1})
            cnx.rollback()


class CommentTC(AutoPopulateTest):
    no_auto_populate = ('TestInstance',)
    ignored_relations = set(('nosy_list',))

    def test_comment_root(self):
        """comments in Forge require that a project property is defined on commentable object
        """
        self.auto_populate(1)
        rschema = self.schema.rschema('comments')
        with self.admin_access.client_cnx() as cnx:
            for etype in rschema.objects():
                if etype == 'TestInstance':
                    continue
                eid = cnx.execute('Any X LIMIT 1 WHERE X is %s' % etype)[0][0]
                comment = cnx.execute('INSERT Comment C: C content "a comment", C comments X WHERE X eid %(x)s',
                                      {'x': eid}).get_entity(0, 0)
                try:
                    comment.project
                except AttributeError:
                    self.fail('%s class does not implement the project property' % etype)


class FTITC(TrackerBaseTC):
    configcls = PostgresApptestConfiguration

    def test_entity_weight(self):
        with self.admin_access.client_cnx() as cnx:
            comment = cnx.create_entity('Comment', content=u'cubicweb comment')
            ticket = cnx.create_entity('Ticket', title=u'bug in cubicweb',
                                       reverse_comments=comment,
                                       concerns=self.cubicweb)
            cnx.commit()
            self.assertEqual([[self.cubicweb], [ticket.eid], [comment.eid]],
                             cnx.execute('Any X ORDERBY FTIRANK(X) DESC WHERE X has_text "cubicweb"').rows)



if __name__ == '__main__':
    unittest_main()
