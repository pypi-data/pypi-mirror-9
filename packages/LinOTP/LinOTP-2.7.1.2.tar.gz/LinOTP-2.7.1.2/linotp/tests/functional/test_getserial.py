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
from linotp.tests import TestController, url

log = logging.getLogger(__name__)

class TestGetSerialController(TestController):

    ###############################################################################
    @classmethod
    def setUpClass(cls):
        ## here we do the system test init (once for all)
        return


    @classmethod
    def tearDownClass(cls):
        print



    def setUp(self):
        self.initToken()

    def tearDown(self):
        pass

    ###############################################################################

    def createHOtpToken(self, hashlib, serial):
        '''
        // Seed for HMAC-SHA1 - 20 bytes
        String seed = "3132333435363738393031323334353637383930";
        // Seed for HMAC-SHA256 - 32 bytes
        String seed32 = "3132333435363738393031323334353637383930" +
        "313233343536373839303132";
        // Seed for HMAC-SHA512 - 64 bytes
        String seed64 = "3132333435363738393031323334353637383930" +
        "3132333435363738393031323334353637383930" +
        "3132333435363738393031323334353637383930" +
        "31323334";
        '''
        ##

        if (hashlib == "SHA512"):
            otpkey = "31323334353637383930313233343536373839303132333435363738393031323334353637383930313233343536373839303132333435363738393031323334"
        elif (hashlib == "SHA256"):
            otpkey = "3132333435363738393031323334353637383930313233343536373839303132"
        else:
            otpkey = "3132333435363738393031323334353637383930"
        parameters = {
                          "serial"  : serial,
                          "type"    : "HMAC",
                          # 64 byte key
                          "otpkey"  : otpkey,
                          "otppin"  : "1234",
                          "pin"     : "pin",
                          "otplen"  : 6,
                          "description" : "time based HMAC TestToken1",
                          "hashlib": hashlib,
                          }


        response = self.app.get(url(controller='admin', action='init'), params=parameters)
        assert '"value": true' in response


    def removeTokenBySerial(self, serial):

        parameters = {
                      "serial": serial,
                      }

        response = self.app.get(url(controller='admin', action='remove'), params=parameters)
        return response



    def setTokenRealm(self, serial, realms):
        parameters = { "serial" : serial,
                       "realms" : realms}

        response = self.app.get(url(controller="admin", action="tokenrealm"), params=parameters)
        return response


    def initToken(self):
        '''
        init two tokens in two realms
        '''

        self.createHOtpToken("SHA1", "oath_mydef")
        '''
        Your OTP with number 2 is 359152.
        Your OTP with number 3 is 969429.
        Your OTP with number 4 is 338314.
        Your OTP with number 5 is 254676.
        Your OTP with number 6 is 287922.
        '''
        self.createHOtpToken("SHA256", "oath_myrealm")
        '''
        Your OTP with number 2 is 072768.
        Your OTP with number 3 is 797306.
        Your OTP with number 4 is 038285.
        Your OTP with number 5 is 143665.
        '''

        # create resolvers - this is a legacy interface
        # but as this is still used in the web gui, we leave this here
        parameters = { "passwdresolver.fileName.mdef" : "%(here)s/../data/testdata/def-passwd",
                       "passwdresolver.fileName.mrealm" :"%(here)s/../data/testdata/def-passwd" }
        resp = self.app.get(url(controller="system", action="setConfig"), parameters)
        print resp
        assert '"status": true' in resp

        # create realms
        parameters = { "realm" : "mydef",
                       "resolvers" : "useridresolver.PasswdIdResolver.IdResolver.mdef" }
        resp = self.app.get(url(controller="system", action="setRealm"), parameters)
        print resp
        assert '"status": true' in resp

        ## legacy syntax for resolver reference
        parameters = { "realm" : "myrealm",
                       "resolvers" : "useridresolver.passwdresolver.mrealm" }
        resp = self.app.get(url(controller="system", action="setRealm"), parameters)
        print resp
        assert '"status": true' in resp

        resp = self.setTokenRealm("oath_mydef", "mydef")
        print resp
        assert '"status": true' in resp
        resp = self.setTokenRealm("oath_myrealm", "myrealm")
        print resp
        assert '"status": true' in resp


    #def test_02_check_realms(self):
    #
    #    parameters = {}
    #    response = self.app.get(url(controller='admin', action='show'),params=parameters)
    #    print response
    #    #assert '"LinOtp.RealmNames": [\n"myrealm"\n]' in resp

    def test_02_token01_success(self):
        '''
        test for the otp of the first token, with all realms
        '''

        parameters = {'otp' : '359152'}
        response = self.app.get(url(controller='admin', action='getSerialByOtp'), params=parameters)
        print response
        assert '"serial": "oath_mydef"' in response



        '''
        test for the otp of the first token, with only in realm mydef
        But it fails, due to same OTP value!
        '''

        parameters = {'otp' : '359152',
                      'realm': 'mydef'}
        response = self.app.get(url(controller='admin', action='getSerialByOtp'), params=parameters)
        print response
        assert '"serial": ""' in response

        '''
        test for the otp of the first token, with only in realm mydef
        '''
        parameters = {'otp' : '969429',
                      'realm': 'mydef'}
        response = self.app.get(url(controller='admin', action='getSerialByOtp'), params=parameters)
        print response
        assert '"serial": "oath_mydef"' in response


        '''
        The OTP of the first token shall not be found in the second realm
        '''

        parameters = {'otp' : '338314',
                      'realm': 'myrealm'}
        response = self.app.get(url(controller='admin', action='getSerialByOtp'), params=parameters)
        print response
        assert '"serial": ""' in response

