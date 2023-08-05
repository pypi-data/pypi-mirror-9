"""some utilities for testing tracker security

:organization: Logilab
:copyright: 2008-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb import Unauthorized, ValidationError
from cubicweb.devtools import BaseApptestConfiguration
from cubicweb.devtools.testlib import CubicWebTC

def create_project_rql(pname, description=None):
    return 'INSERT Project X: X name %(name)s, X description %(descr)s', \
           {'name': unicode(pname), 'descr': unicode(description)}

def create_version_rql(num, pname):
    return 'INSERT Version X: X num %(num)s, X version_of P '\
           'WHERE P name %(name)s', \
           {'num': unicode(num), 'name': unicode(pname)}

def create_ticket_rql(title, pname):
    return 'INSERT Ticket X: X title %(title)s, X concerns P '\
           'WHERE P name %(name)s', \
           {'title': unicode(title), 'name': unicode(pname)}


# XXX take both TestCase *class* and session (need for both since session only
# available on TestCase *instance*)
def security_tc_init_project(tc, cnx, name, user_prefix=None):
    project = cnx.execute(*create_project_rql(name)).get_entity(0, 0)
    if user_prefix is None:
        user_prefix = name
    for perm in (u'developer', u'client'):
        group = "%s%ss" % (name, perm)
        cnx.create_entity('CWGroup', name=group)
        tc.grant_permission(cnx, project, group, perm)
        tc.create_user(cnx, '%s%s' % (user_prefix, perm), groups=('users', group,),
                       commit=False)
    return project


class TrackerTCMixIn(object):

    def create_project(self, cnx, pname, description=None):
        return cnx.execute(*create_project_rql(pname, description))

    def create_version(self, cnx, num, pname='cubicweb'):
        return cnx.execute(*create_version_rql(num, pname))

    def create_ticket(self, cnx, title, vnum=None, pname='cubicweb'):
        rset = cnx.execute(*create_ticket_rql(title, pname))
        if vnum:
            cnx.execute('SET X done_in V WHERE X eid %(x)s, V num %(num)s',
                        {'x': rset[0][0], 'num': vnum})
        return rset


class TrackerBaseTC(TrackerTCMixIn, CubicWebTC):

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            self.cubicweb = cnx.create_entity('Project', name=u'cubicweb',
                                              description=u"cubicweb c'est beau").eid
            cnx.commit()

    def tearDown(self):
        CubicWebTC.tearDown(self)
        self.repo.close_sessions()


class SecurityTC(TrackerTCMixIn, CubicWebTC):
    repo_config = BaseApptestConfiguration('data')

    def setUp(self):
        """
            User created:
                - stduser
                - staffuser
                - prj1developer
                - prj1client
                - prj2developer
                - prj2client
        """
        CubicWebTC.setUp(self)
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, 'stduser')
            self.create_user(cnx, 'staffuser', groups=('users', 'staff',))
            self.cubicweb = security_tc_init_project(self, cnx, 'cubicweb', user_prefix='prj1').eid
            self.project2 = security_tc_init_project(self, cnx, 'project2', user_prefix='prj2').eid
            cnx.commit()
            self.maxeid = cnx.execute('Any MAX(X)')[0][0]

    def tearDown(self):
        CubicWebTC.tearDown(self)
        self.repo.close_sessions()

    def _test_tr_fail(self, user, x, trname):
        with self.new_access(user).client_cnx() as cnx:
            entity = cnx.entity_from_eid(x)
            # if the user can't see entity x, Unauthorized is raised, else if he
            # can't pass the transition, Validation is raised
            self.assertRaises((Unauthorized, ValidationError),
                              entity.cw_adapt_to('IWorkflowable').fire_transition, trname)

    def _test_tr_success(self, user, x, trname):
        with self.new_access(user).client_cnx() as cnx:
            entity = cnx.entity_from_eid(x)
            entity.cw_adapt_to('IWorkflowable').fire_transition(trname)
            cnx.commit()
