# -*- coding: utf-8 -*-
#
#    LinOTP - the open source solution for two factor authentication
#    Copyright (C) 2010 - 2015 LSE Leading Security Experts GmbH
#
#    This file is part of LinOTP server.
#
#    This program is free software: you can redistribute it and/or
#    modify it under the terms of the GNU Affero General Public
#    License, version 3, as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the
#               GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    E-mail: linotp@lsexperts.de
#    Contact: www.linotp.org
#    Support: www.lsexperts.de
#


"""
"""


import logging
try:
    import json
except ImportError:
    import simplejson

from linotp.tests import TestController, url

log = logging.getLogger(__name__)

class TestManageController(TestController):


    def setUp(self):
        '''
        resolver: reso1 (my-passwd), reso2 (my-pass2)
        realm: realm1, realm2
        token: token1 (r1), token2 (r1), token3 (r2)
        '''

        ## remove all other tokens
        self.deleteAllTokens()

        # create resolvers
        response = self.app.get(url(controller='system', action='setResolver'),
                                params={'name':'reso1',
                                        'type': 'passwdresolver',
                                        'fileName': 'my-passwd'})
        print response
        assert '"value": true' in response

        response = self.app.get(url(controller='system', action='setResolver'),
                                params={'name':'reso2',
                                        'type': 'passwdresolver',
                                        'fileName': 'my-pass2'})
        print response
        assert '"value": true' in response

        # create realms

        response = self.app.get(url(controller='system', action='setRealm'),
                                params={'realm': 'realm1',
                                        'resolvers': 'useridresolver.PasswdIdResolver.IdResolver.reso1'})
        print response
        assert '"value": true' in response

        response = self.app.get(url(controller='system', action='setRealm'),
                                params={'realm': 'realm2',
                                        'resolvers': 'useridresolver.PasswdIdResolver.IdResolver.reso2'})
        print response
        assert '"value": true' in response

        # create token
        response = self.app.get(url(controller='admin', action='init'),
                                params={'serial' : 'token1',
                                        'type' : 'spass',
                                        'pin' : 'secret',
                                        'user': 'heinz',
                                        'realm': 'realm1'
                                        })
        print response
        assert '"value": true' in response

        response = self.app.get(url(controller='admin', action='init'),
                                params={'serial' : 'token2',
                                        'type' : 'spass',
                                        'pin' : 'secret',
                                        'user': 'nick',
                                        'realm': 'realm1'
                                        })
        print response
        assert '"value": true' in response


        response = self.app.get(url(controller='admin', action='init'),
                                params={'serial' : 'token3',
                                        'type' : 'spass',
                                        'pin' : 'secret',
                                        'user': 'renate',
                                        'realm': 'realm2'
                                        })
        print response
        assert '"value": true' in response




    ###############################################################################
    def test_index(self):
        '''
        Manage: testing index access
        '''
        response = self.app.get(url(controller='manage', action='index'),
                                params={})
        print "index response: %r" % response.testbody
        assert '<title>LinOTP 2 Management</title>' in response.testbody


    def test_policies(self):
        '''
        Manage: testing policies tab
        '''
        response = self.app.get(url(controller='manage', action='policies'),
                                params={})
        print "policies response: %r" % response.testbody
        assert '<a id=policy_export>' in response.testbody
        assert '<button id=policy_import>' in response.testbody
        assert '<button id="button_policy_delete">' in response.testbody

    def test_audit(self):
        '''
        Manage: testing audit trail
        '''
        response = self.app.get(url(controller='manage', action='audittrail'),
                                params={})
        print "audit response: %r" % response.testbody
        assert 'table id="audit_table"' in response.testbody
        assert 'view_audit();' in response.testbody

    def test_tokenview(self):
        '''
        Manage: testing tokenview
        '''
        response = self.app.get(url(controller='manage', action='tokenview'),
                                params={})
        print "token response: %r" % response.testbody
        assert 'button_losttoken' in response.testbody
        assert 'button_tokeninfo' in response.testbody
        assert 'button_resync' in response.testbody
        assert 'button_tokenrealm' in response.testbody
        assert 'table id="token_table"' in response.testbody
        assert 'view_token();' in response.testbody
        assert 'tokenbuttons();' in response.testbody

    def test_userview(self):
        '''
        Manage: testing userview
        '''
        response = self.app.get(url(controller='manage', action='userview'),
                                params={})
        print "user response: %r" % response.testbody
        assert 'table id="user_table"' in response.testbody
        assert 'view_user();' in response.testbody

    def test_tokenflexi(self):
        '''
        Manage: testing the tokenview_flexi method
        '''
        response = self.app.get(url(controller='manage', action='tokenview_flexi'),
                                params={})

        testbody = response.body.replace('\n', ' ').replace('\r', '').replace("  ", " ")
        print "token flexi response 1: %r" % response.testbody
        assert '"total": 3' in testbody
        assert '"token1",       true,       "heinz"' in testbody
        assert '"token2",       true,       "nick"' in testbody
        assert '"token3",       true,       "renate"' in testbody

        # only renates token
        response = self.app.get(url(controller='manage', action='tokenview_flexi'),
                                params={'qtype' : 'loginname',
                                        'query' : 'renate'})
        testbody = response.body.replace('\n', ' ').replace('\r', '').replace("  ", " ")
        print "token flexi response 2: %r" % response.testbody
        assert '"total": 1' in testbody
        assert '"token3",       true,       "renate"' in testbody

        # only tokens in realm1
        response = self.app.get(url(controller='manage', action='tokenview_flexi'),
                                params={'qtype' : 'realm',
                                        'query' : 'realm1'})
        print "token flexi response 3: %r" % response.testbody
        assert '"total": 2' in response.testbody
        testbody = response.body.replace('\n', ' ').replace('\r', '').replace("  ", " ")
        assert '"token1",       true,       "heinz"' in testbody
        assert '"token2",       true,       "nick"' in testbody

        # search in all columns
        response = self.app.get(url(controller='manage', action='tokenview_flexi'),
                                params={'qtype' : 'all',
                                        'query' : 'token2'})
        print "token flexi response 4: %r" % response.testbody
        assert '"total": 1' in response.testbody
        testbody = response.body.replace('\n', ' ').replace('\r', '').replace("  ", " ")
        assert '"token2",       true,       "nick"' in testbody

    def test_userflexi(self):
        '''
        Manage: testing the userview_flexi method
        '''
        # No realm, no user
        response = self.app.get(url(controller='manage', action='userview_flexi'),
                                params={})
        print "user flexi response 1: %r" % response.testbody
        assert '"total": 0' in response.testbody

        # No realm, no user

        response = self.app.get(url(controller='manage', action='userview_flexi'),
                                params={"page" :1,
                                        "rp": 15,
                                        "sortname": "username",
                                        "sortorder": "asc",
                                        "query": "",
                                        "qtype": "username",
                                        "realm": "realm1"})
        print "user flexi response 2: %r" % response.testbody
        assert '"id": "heinz"' in response.testbody


        response = self.app.get(url(controller='manage', action='userview_flexi'),
                                params={"page" :1,
                                        "rp": 15,
                                        "sortname": "username",
                                        "sortorder": "desc",
                                        "query": "",
                                        "qtype": "username",
                                        "realm": "realm2"})
        print "user flexi response 3: %r" % response.testbody
        assert '"id": "renate"' in response.testbody


    def test_tokeninfo(self):
        '''
        Manage: Testing tokeninfo dialog
        '''
        response = self.app.get(url(controller='manage', action='tokeninfo'),
                                params={"serial" : "token1"})
        print "tokeninfo response: %r" % response.testbody
        assert 'class=tokeninfoOuterTable' in response.testbody
        assert 'Heinz Hirtz' in response.testbody
        assert 'Heinz Hirtz' in response.testbody
        assert '<td class=tokeninfoOuterTable>LinOtp.TokenSerialnumber</td>\n    \t<!-- middle column -->\n    <td class=tokeninfoOuterTable>\n    \ttoken1\n    </td>\n        \t<!-- right column -->' in response.testbody


    def test_logout(self):
        '''
        Manage: testing logout
        '''
        response = self.app.get(url(controller='manage', action='logout'),
                                params={})
        print "logout response: %r" % response.testbody
        assert '302 Found\n\nThe resource was found at' in response.testbody

