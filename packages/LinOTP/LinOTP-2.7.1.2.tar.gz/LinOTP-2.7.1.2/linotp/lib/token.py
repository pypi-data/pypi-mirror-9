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
""" contains several token api functions"""

import traceback
import string
import datetime
import sys
import re
import binascii

import os
import logging


try:
    import json
except ImportError:
    import simplejson as json

from sqlalchemy import or_, and_, not_
from sqlalchemy import func


from pylons import tmpl_context as c
from pylons.i18n.translation import _
from pylons import config

from linotp.lib.error import TokenAdminError
from linotp.lib.error import UserError
from linotp.lib.error import ParameterError

from linotp.lib.user import getUserId, getUserInfo
from linotp.lib.user import User, getUserRealms
from linotp.lib.user import check_user_password

from linotp.lib.util import getParam
from linotp.lib.util import generate_password
from linotp.lib.util import modhex_decode

from linotp.lib.realm import realm2Objects
from linotp.lib.realm import getRealms

import linotp
import linotp.lib.policy

from linotp import model
from linotp.model import Token, createToken, Realm, TokenRealm
from linotp.model.meta import Session
from linotp.model import Challenge

from linotp.lib.config  import getFromConfig
from linotp.lib.resolver import getResolverObject

from linotp.lib.realm import createDBRealm, getRealmObject
from linotp.lib.realm import getDefaultRealm

from linotp.lib.util import get_client

log = logging.getLogger(__name__)

optional = True
required = False

ENCODING = "utf-8"

###############################################
def createTokenClassObject(token, typ=None):
    '''
    createTokenClassObject - create a token class object from a given type

    :param token:  the database refeneced token
    :type  token:  database token
    :param typ:    type of to be created token
    :type  typ:    string

    :return: instance of the token class object
    :rtype:  token class object
    '''

    # if type is not given, we take it out of the token database object
    if (typ is None):
        typ = token.LinOtpTokenType

    if typ == "":
        typ = "hmac"

    typ = typ.lower()
    tok = None

    # search which tokenclass should be created and create it!
    tokenclasses = config['tokenclasses']
    if tokenclasses.has_key(typ.lower()):
        try:
            token_class = tokenclasses.get(typ)
            tok = newToken(token_class)(token)
        except Exception as e:
            log.debug('createTokenClassObject failed!')
            raise TokenAdminError("createTokenClassObject failed:  %r" % e, id=1609)

    else:
        log.error('[createTokenClassObject] typ %r not found in tokenclasses: %r' %
                  (typ, tokenclasses))
        #
        ## we try to use the parent class, which is able to handle most of the
        ## administrative tasks. This will allow to unassigen and disable or delete
        ## this 'abandoned token'
        #
        from linotp.lib.tokenclass import TokenClass
        tok = TokenClass(token)
        log.error("[createTokenClassObject] failed: unknown token type %r. \
                 Using fallback 'TokenClass' for %r" % (typ, token))

    return tok

def newToken(token_class):
    '''
    newTokenClass - return a token class, which could be used as a constructor

    :param token_class: string representation of the token class name
    :type   token_class: string
    :return: token class
    :rtype:  token class

    '''

    ret = ""
    attribute = ""

    ## prepare the lookup
    parts = token_class.split('.')
    package_name = '.'.join(parts[:-1])
    class_name = parts[-1]

    if sys.modules.has_key(package_name):
        mod = sys.modules.get(package_name)
    else:
        mod = __import__(package_name, globals(), locals(), [class_name])
    try:
        klass = getattr(mod, class_name)

        attrs = ["getType", "checkOtp"]
        for att in attrs:
            attribute = att
            getattr(klass, att)

        ret = klass
    except:
        raise NameError(
            "IdResolver AttributeError: " + package_name + "." + class_name
             + " instance has no attribute '" + attribute + "'")
    return ret


def get_token_type_list():
    '''
    get_token_type_list - returns the list of the available tokentypes like hmac, spass, totp...

    :return: list of token types
    :rtype : list
    '''

    try:
#        from linotp.lib.config      import getGlobalObject
        tokenclasses = config['tokenclasses']

    except Exception as e:
        log.debug('get_token_type_list failed!')
        raise TokenAdminError("get_token_type_list failed:  %r" % e, id=1611)

    token_type_list = tokenclasses.keys()
    return token_type_list



def getRealms4Token(user, tokenrealm=None):
    '''
    get the realm objects of a user or from the tokenrealm defintion,
    which could be a list of realms or a single realm
     - helper method to enhance the code readablility

    :param user: the user wich defines the set of realms
    :param tokenrealm: a string or a list of realm strings

    :return: the list of realm objects
    '''

    realms = []
    if user is not None and user.login != "" :
        ## the getUserRealms should return the default realm if realm was empty
        realms = getUserRealms(user)
        ## hack: sometimes the realm of the user is not in the
        ## realmDB - so check and add
        for r in realms:
            realmObj = getRealmObject(name=r)
            if realmObj is None:
                createDBRealm(r)

    if tokenrealm is not None:
        # tokenrealm can either be a string or a list
        log.debug("[getRealms4Token] tokenrealm given (%r). We will add the "
                  "new token to this realm" % tokenrealm)
        if isinstance(tokenrealm, str):
            log.debug("[getRealms4Token] String: adding realm: %r" % tokenrealm)
            realms.append(tokenrealm)
        elif isinstance(tokenrealm, list):
            for tr in tokenrealm:
                log.debug("[getRealms4Token] List: adding realm: %r" % tr)
                realms.append(tr)

    realmList = realm2Objects(realms)

    return realmList

def get_tokenserial_of_transaction(transId):
    '''
    get the serial number of a token from a challenge state / transaction

    :param transId: the state / transaction id
    :return: the serial number or None
    '''
    serial = None

    challenges = Session.query(Challenge)\
                .filter(Challenge.transid == u'' + transId).all()

    if len(challenges) == 0:
        log.info('no challenge found for tranId %r' % (transId))
        return None
    elif len(challenges) > 1:
        log.info('multiple challenges found for tranId %r' % (transId))
        return None

    serial = challenges[0].tokenserial

    return serial


def initToken(param, user, tokenrealm=None):
    '''
    initToken - create a new token or update a token

    :param param: the list of provided parameters
                  in the list the serialnumber is required,
                  the token type default ist hmac
    :param user:  the token owner
    :param tokenrealm: the realms, to which the token belongs

    :return: tuple of success and token object
    '''
    log.debug("[initToken] begin. create token with param %r for user %r and\
                tokenrealm %r" % (param, user, tokenrealm))

    token = None
    tokenObj = None

    typ = getParam(param, "type", optional)
    if typ is None:
        typ = "hmac"

    #serial = getParam(param, "serial", required)
    serial = param.get('serial', None)
    if serial is None:
        prefix = param.get('prefix', None)
        serial = genSerial(typ, prefix)



    # if a token was initialized for a user, the param "realm" might be contained.
    # otherwise - without a user the param tokenrealm could be contained.
    log.debug("[initToken] initilizing token %r for user %r " % (serial, user.login))

    ## create a list of the found db tokens - no token class objects
    toks = getTokens4UserOrSerial(None, serial, _class=False)
    tokenNum = len(toks)

    tokenclasses = config['tokenclasses']

    if tokenNum == 0:  ## create new a one token
        ## check if this token is in the list of available tokens
        if not tokenclasses.has_key(typ.lower()):
            log.error('[initToken] typ %r not found in tokenclasses: %r' %
                      (typ, tokenclasses))
            raise TokenAdminError("[initToken] failed: unknown token type %r" % typ , id=1610)
        token = createToken(serial)

    elif tokenNum == 1:  # update if already there
        token = toks[0]

        # prevent from changing the token type
        old_typ = token.LinOtpTokenType
        if old_typ.lower() != typ.lower():
            msg = 'token %r already exist with type %r. Can not initialize token with new type %r' % (serial, old_typ, typ)
            log.error('[initToken] %s' % msg)
            raise TokenAdminError("initToken failed: %s" % msg)

        ## prevent update of an unsupported token type
        if not tokenclasses.has_key(typ.lower()):
            log.error('[initToken] typ %r not found in tokenclasses: %r' %
                      (typ, tokenclasses))
            raise TokenAdminError("[initToken] failed: unknown token type %r" % typ , id=1610)

    else:  ## something wrong
        if tokenNum > 1:
            raise TokenAdminError("multiple tokens found - cannot init!", id=1101)
        else:
            raise TokenAdminError("cannot init! Unknown error!", id=1102)

    ## if there is a realm as parameter, we assign the token to this realm
    if 'realm' in param:
        ## if we get a undefined tokenrealm , we create a list
        if tokenrealm is None:
            tokenrealm = []
        ## if we get a tokenrealm as string, we make an array out of this
        elif type(tokenrealm) in [str, unicode]:
            tokenrealm = [tokenrealm]
        ## and append our parameter realm
        tokenrealm.append(param.get('realm'))

    ## get the RealmObjects of the user and the tokenrealms
    realms = getRealms4Token(user, tokenrealm)
    token.setRealms(realms)

    ## on behalf of the type, the class is created
    tokenObj = createTokenClassObject(token, typ)

    if tokenNum == 0:
        ## if this token is a newly created one, we have to setup the defaults,
        ## which lateron might be overwritten by the tokenObj.update(params)
        tokenObj.setDefaults()

    tokenObj.update(param)


    if user is not None and user.login != "" :
        tokenObj.setUser(user, report=True)

    try:
        token.storeToken()
    except Exception as e:
        log.error('[initToken] token create failed!')
        log.error("[initToken] %r" % (traceback.format_exc()))
        raise TokenAdminError("token create failed %r" % e, id=1112)

    log.debug("[initToken] end. created tokenObject %r and returning status %r "
              % (True, tokenObj))
    return (True, tokenObj)

def getRolloutToken4User(user=None, serial=None, tok_type=u'ocra'):

    if (user is None or user.isEmpty()) and serial is None:
        return None

    serials = []
    tokens = []

    if user is not None and user.isEmpty() == False:
        resolverUid = user.resolverUid
        v = None
        k = None
        for k in resolverUid:
            v = resolverUid.get(k)
        user_id = v

        # in the database could be tokens of ResolverClass:
        #    useridresolver. or useridresolveree.
        # so we have to make sure
        # - there is no 'useridresolveree' in the searchterm and
        # - there is a wildcard search: second replace
        # Remark: when the token is loaded the response to the
        # resolver class is adjusted

        user_resolver = k.replace('useridresolveree.', 'useridresolver.')
        user_resolver = user_resolver.replace('useridresolver.', 'useridresolver%.')

        ''' coout tokens: 0 1 or more '''
        tokens = Session.query(Token).filter(Token.LinOtpTokenType == unicode(tok_type))\
                                       .filter(Token.LinOtpIdResClass.like(unicode(user_resolver)))\
                                       .filter(Token.LinOtpUserid == unicode(user_id))

    elif serial is not None:
        tokens = Session.query(Token).filter(Token.LinOtpTokenType == unicode(tok_type))\
                                       .filter(Token.LinOtpTokenSerialnumber == unicode(serial))

    for token in tokens:
        info = token.LinOtpTokenInfo
        if len(info) > 0:
            tinfo = json.loads(info)
            rollout = tinfo.get('rollout', None)
            if rollout is not None:
                serials.append(token.LinOtpTokenSerialnumber)


    if len(serials) > 1:
        raise Exception('multiple tokens found in rollout state: %s'
                        % unicode(serials))

    if len(serials) == 1:
        serial = serials[0]

    return serial

def setRealms(serial, realmList):
    # set the tokenlist of DB tokens
    tokenList = getTokens4UserOrSerial(None, serial, _class=False)

    if len(tokenList) == 0:
        log.error("[setRealms] No token with serial %r found." % serial)
        raise TokenAdminError("setRealms failed. No token with serial %s found"
                              % serial, id=1119)

    realmObjList = realm2Objects(realmList)

    for token in tokenList:
        token.setRealms(realmObjList)

    return len(tokenList)

def getTokenRealms(serial):
    '''
    This function returns a list of the realms of a token
    '''
    tokenList = getTokens4UserOrSerial(None, serial, _class=False)

    if len(tokenList) == 0:
        log.error("[getTokenRealms] No token with serial %r found." % serial)
        raise TokenAdminError("getTokenRealms failed. No token with serial %s found" % serial, id=1119)

    token = tokenList[0]

    return token.getRealmNames()

def getRealmsOfTokenOrUser(token):
    '''
    This returns the realms of either the token or
    of the user of the token.
    '''
    serial = token.getSerial()
    realms = getTokenRealms(serial)

    if len(realms) == 0:
        uid, resolver, resolverClass = token.getUser()
        log.debug("[getRealmsOfTokenOrUser] %r, %r, %r" % (uid, resolver, resolverClass))
        # No realm and no User, this is the case in /validate/check_s
        if resolver.find('.') >= 0:
            resotype, resoname = resolver.rsplit('.', 1)
            realms = getUserRealms(User("dummy_user", "", resoname))

    log.debug("[getRealmsOfTokenOrUser] the token %r "
              "is in the following realms: %r" % (serial, realms))

    return realms


def getTokenInRealm(realm, active=True):
    '''
    This returns the number of tokens in one realm.

    You can either query only active token or also disabled tokens.
    '''
    if active:
        sqlQuery = Session.query(TokenRealm, Realm, Token).filter(and_(
                            TokenRealm.realm_id == Realm.id,
                            Realm.name == u'' + realm,
                            Token.LinOtpIsactive == True,
                            TokenRealm.token_id == Token.LinOtpTokenId)).count()
    else:
        sqlQuery = Session.query(TokenRealm, Realm).filter(and_(
                            TokenRealm.realm_id == Realm.id,
                            Realm.name == realm)).count()
    return sqlQuery

def getTokenNumResolver(resolver=None, active=True):
    '''
    This returns the number of the (active) tokens
    if no resolver is passed, the overall token number is returned,
    if a resolver is passed, the token number within this resolver is returned

    if active is set to false, ALL tokens are returned
    '''
    if resolver is None:
        if active:
            sqlQuery = Session.query(Token).filter(Token.LinOtpIsactive == True).count()
        else:
            sqlQuery = Session.query(Token).count()
        return sqlQuery
    else:
        # in the database could be tokens of ResolverClass:
        #    useridresolver. or useridresolveree.
        # so we have to make sure
        # - there is no 'useridresolveree' in the searchterm and
        # - there is a wildcard search: second replace
        # Remark: when the token is loaded the response to the
        # resolver class is adjusted

        resolver = resolver.resplace('useridresolveree.', 'useridresolver.')
        resolver = resolver.resplace('useridresolver.', 'useridresolver%.')

        if active:
            sqlQuery = Session.query(Token).filter(and_(Token.LinOtpIdResClass.like(resolver), Token.LinOtpIsactive == True)).count()
        else:
            sqlQuery = Session.query(Token).filter(Token.LinOtpIdResClass.like(resolver)).count()
        return sqlQuery

def getAllTokenUsers():
    '''
        return a list of all users
    '''
    users = {}
    sqlQuery = Session.query(Token)
    for token in sqlQuery:
        userInfo = {}

        log.debug("[getAllTokenUsers] user serial (serial): %r" % token.LinOtpTokenSerialnumber)

        serial = token.LinOtpTokenSerialnumber
        userId = token.LinOtpUserid
        resolver = token.LinOtpIdResolver
        resolverC = token.LinOtpIdResClass

        if len(userId) > 0 and len(resolver) > 0:
            userInfo = getUserInfo(userId, resolver, resolverC)

        if len(userId) > 0 and len(userInfo) == 0:
            userInfo['username'] = u'/:no user info:/'

        if len(userInfo) > 0:
            users[serial] = userInfo

    return users

def getTokens4UserOrSerial(user=None, serial=None, forUpdate=False, _class=True):
    tokenList = []
    tokenCList = []
    tok = None

    if serial is None and user is None:
        log.warning("[getTokens4UserOrSerial] missing user or serial")
        return tokenList

    if (serial is not None):
        log.debug("[getTokens4UserOrSerial] getting token object "
                                                "with serial: %r" % serial)
        ## SAWarning of non unicode type
        serial = linotp.lib.crypt.uencode(serial)

        sqlQuery = Session.query(Token).filter(
                            Token.LinOtpTokenSerialnumber == serial)

        if forUpdate == True:
            sqlQuery = Session.query(Token).with_lockmode("update").filter(
                            Token.LinOtpTokenSerialnumber == serial)

        #for token in Session.query(Token).filter(Token.LinOtpTokenSerialnumber == serial):
        for token in sqlQuery:
            log.debug("[getTokens4UserOrSerial] user "
                      "serial (serial): %r" % token.LinOtpTokenSerialnumber)
            tokenList.append(token)

    if user is not None:
        log.debug("[getTokens4UserOrSerial] getting token object 4 user: %r" % user)

        if (user.isEmpty() == False):
            # the upper layer will catch / at least should
            (uid, resolver, resolverClass) = getUserId(user)

            # in the database could be tokens of ResolverClass:
            #    useridresolver. or useridresolveree.
            # so we have to make sure
            # - there is no 'useridresolveree' in the searchterm and
            # - there is a wildcard search: second replace
            # Remark: when the token is loaded the response to the
            # resolver class is adjusted

            resolverClass = resolverClass.replace('useridresolveree.', 'useridresolver.')
            resolverClass = resolverClass.replace('useridresolver.', 'useridresolver%.')

            sqlQuery = Session.query(model.Token).filter(
                        model.Token.LinOtpUserid == uid).filter(
                        model.Token.LinOtpIdResClass.like(resolverClass))
            if forUpdate == True:
                sqlQuery = Session.query(model.Token).with_lockmode("update").filter(
                            model.Token.LinOtpUserid == uid).filter(
                            model.Token.LinOtpIdResClass.like(resolverClass))

            for token in sqlQuery:
                log.debug("[getTokens4UserOrSerial] user serial (user): %r"
                          % token.LinOtpTokenSerialnumber)
                tokenList.append(token)

    if _class == True:
        for tok in tokenList:
            tokenCList.append(createTokenClassObject(tok))
        return tokenCList
    else:
        return tokenList

def getTokensOfType(typ=None, realm=None, assigned=None):
    '''
    This function returns a list of token objects of the following type.

    here we need to create the token list.
       1. all types (if typ==None)
       2. realms
       3. assigned or unassigned tokens (1/0)
    TODO: rename function to "getTokens"
    '''
    tokenList = []
    log.debug("[getTokensOfType] searching tokens type=%r, realm=%r, assigned=%r" % (typ, realm, assigned))
    sqlQuery = Session.query(Token)
    if typ is not None:
        # filter for type
        sqlQuery = sqlQuery.filter(func.lower(Token.LinOtpTokenType) == typ.lower())
    if assigned is not None:
        # filter if assigned or not
        if "0" == unicode(assigned):
            sqlQuery = sqlQuery.filter(or_(Token.LinOtpUserid == None,
                                           Token.LinOtpUserid == ""))
        elif "1" == unicode(assigned):
            sqlQuery = sqlQuery.filter(func.length(Token.LinOtpUserid) > 0)
        else:
            log.warning("[getTokensOfType] assigned value not in [0,1] %r" % assigned)

    if realm is not None:
        # filter for the realm
        sqlQuery = sqlQuery.filter(and_(func.lower(Realm.name) == realm.lower(),
                                        TokenRealm.realm_id == Realm.id,
                                        TokenRealm.token_id == Token.LinOtpTokenId)).distinct()

    for token in sqlQuery:
        log.debug("[getTokensOfType] adding token with serial %r" % token.LinOtpTokenSerialnumber)
        # the token is the database object, but we want an instance of the tokenclass!
        tokenList.append(createTokenClassObject(token))

    return tokenList

def setDefaults(token):
    ## set the defaults

    token.LinOtpOtpLen = int(getFromConfig("DefaultOtpLen", 6))
    token.LinOtpCountWindow = int(getFromConfig("DefaultCountWindow", 15))
    token.LinOtpMaxFail = int(getFromConfig("DefaultMaxFailCount", 15))
    token.LinOtpSyncWindow = int(getFromConfig("DefaultSyncWindow", 1000))

    token.LinOtpTokenType = u"HMAC"


def isTokenOwner(serial, user):
    ret = False

    userid = ""
    idResolver = ""
    idResolverClass = ""

    log.debug("[isTokenOwner] entering function isTokenOwner")

    if user is not None and (user.isEmpty() == False):
    # the upper layer will catch / at least should
        (userid, idResolver, idResolverClass) = getUserId(user)

    if len(userid) + len(idResolver) + len(idResolverClass) == 0:
        log.info("[isTokenOwner] no user found %r", user.login)
        raise TokenAdminError("no user found %s" % user.login, id=1104)

    toks = getTokens4UserOrSerial(None, serial)

    if len(toks) > 1:
        log.info("[isTokenOwner] multiple tokens found for user %r" % user.login)
        raise TokenAdminError("multiple tokens found!", id=1101)
    if len(toks) == 0:
        log.info("[isTokenOwner] no tokens found for user %r", user.login)
        raise TokenAdminError("no token found!", id=1102)

    token = toks[0]

    (uuserid, uidResolver, uidResolverClass) = token.getUser()

    if uidResolver == idResolver:
        if uidResolverClass == idResolverClass:
            if uuserid == userid:
                ret = True

    return ret


def tokenExist(serial):
    '''
    returns true if the token exists
    '''
    log.debug("[tokenExist] checking if Token %r exists" % serial)
    if serial:
        toks = getTokens4UserOrSerial(None, serial)
        return (len(toks) > 0)
    else:
        # If we have no serial we return false anyway!
        log.debug("[tokenExist] returning false anyway")
        return False



def hasOwner(serial):
    '''
    returns true if the token is owned by any user
    '''
    ret = False

    log.debug('[hasOwner] entering function hasOwner()')

    toks = getTokens4UserOrSerial(None, serial)

    if len(toks) > 1:
        log.info("[hasOwner] multiple tokens found with serial %r" % serial)
        raise TokenAdminError("multiple tokens found!", id=1101)
    if len(toks) == 0:
        log.info("[hasOwner] no token found with serial %r" % serial)
        raise TokenAdminError("no token found!", id=1102)

    token = toks[0]

    (uuserid, uidResolver, uidResolverClass) = token.getUser()

    if len(uuserid) + len(uidResolver) + len(uidResolverClass) > 0:
        ret = True

    return ret


def getTokenOwner(serial):
    '''
    returns the user object, to which the token is assigned.
    the token is idetified and retirved by it's serial number

    :param serial: serial number of the token
    :return: user object
    '''
    log.debug("[getTokenOwner] getting token owner for serial: %r" % serial)
    token = None

    toks = getTokens4UserOrSerial(None, serial)
    if len(toks) > 0:
        token = toks[0]

    user = get_token_owner(token)

    return user


def get_token_owner(token):
    """
    provide the owner as a user object for a given tokenclass obj

    :param token: tokenclass object
    :return: user object
    """

    user = User()

    if token is None:
        ## for backward compatibility, we return here an empty user
        return user

    serial = token.getSerial()

    log.debug("[get_token_owner] token found: %r" % token)
    uid, resolver, resolverClass = token.getUser()

    userInfo = getUserInfo(uid, resolver, resolverClass)
    log.debug("[get_token_owner] got the owner %r, %r, %r"
               % (uid, resolver, resolverClass))

    realms = getUserRealms(User(uid, "", resolverClass.split(".")[-1]))
    log.debug("[get_token_owner] got this realms: %r" % realms)

    # if there are several realms, than we need to find out, which one!
    if len(realms) > 1:
        t_realms = getTokenRealms(serial)
        common_realms = list(set(realms).intersection(t_realms))
        if len(common_realms) > 1:
            raise Exception(_("get_token_owner: The user %s/%s and the token"
                              " %s is located in several realms: "
                              "%s!" % (uid, resolverClass, serial, common_realms)))
        realm = common_realms[0]
    elif len(realms) == 0:
        raise Exception(_("get_token_owner: The user %s in the resolver"
                          " %s for token %s could not be found in any "
                          "realm!" % (uid, resolverClass, serial)))
    else:
        realm = realms[0]

    user.realm = realm
    user.login = userInfo.get('username')
    user.conf = resolverClass

    log.debug("[get_token_owner] found the user %r and the realm %r as "
              "owner of token %r" % (user.login, user.realm, serial))

    return user

def getTokenType(serial):
    '''
    Returns the tokentype of a given serial number

    :param serial: the serial number of the to be searched token
    '''
    log.debug("[getTokenType] getting token type for serial: %r" % serial)
    toks = getTokens4UserOrSerial(None, serial, _class=False)

    typ = ""
    for tok in toks:
        typ = tok.LinOtpTokenType

    log.debug("[getTokenType] the token is of type: %r" % typ)

    return typ

def check_serial(serial):
    '''
    This checks, if a serial number is already contained.

    The function returns a tuple:
        (result, new_serial)

    If the serial is already contained a new, modified serial new_serial is returned.

    result: bool: True if the serial does not already exist.
    '''
    # serial does not exist, yet
    result = True
    new_serial = serial
    log.debug("[check_serial] check if token %r already exists" % serial)

    i = 0
    while len(getTokens4UserOrSerial(None, new_serial)) > 0:
        # as long as we find a token, modify the serial:
        i = i + 1
        result = False
        new_serial = "%s_%02i" % (serial, i)

    return (result, new_serial)

def auto_assignToken(passw, user, pin="", param=None):
    '''
    This function is called to auto_assign a token, when the
    user enters an OTP value of an not assigned token.
    '''
    ret = False
    auto = False

    if param is None:
        param = {}

    # Fixme: circle dependency
    try:
        auto, _otplen = linotp.lib.policy.get_autoassignment(user)
    except Exception as e:
        log.error("[auto_assignToken] %r" % e)

    # check if autoassignment is configured
    if not auto:
        log.debug("[auto_assignToken] not autoassigment configured")
        return False

    # check if user has a token
    # TODO: this may dependend on a policy definition
    tokens = getTokens4UserOrSerial(user, "")
    if len(tokens) > 0:
        log.debug("[auto_assignToken] no auto_assigment for user %r@%r. He "
                  "already has some tokens." % (user.login, user.realm))
        return False

    matching_token_count = 0

    token = None
    pin = ""

    ## get all tokens of the users realm, which are not assigned
    tokens = getTokensOfType(typ=None, realm=user.realm, assigned="0")
    for token in tokens:
        (res, pin, otp) = token.splitPinPass(passw)
        if res >= 0:
            r = token.check_otp_exist(otp=otp,
                                      window=token.getOtpCountWindow())
            if r >= 0:
                matching_token_count += 1

    if matching_token_count != 1:
        log.warning("[auto_assignToken] %d tokens with "
                    "the given OTP value found.", matching_token_count)
        return False

    success = check_user_password(user.login, user.realm, pin)
    if success is None:
        log.error("[auto_assignToken] User %r@%r failed to authenticate against userstore" % (user.login, user.realm))
        return False

    serial = token.getSerial()

    log.debug("[auto_assignToken] found serial number: %r" % serial)

    # should the password of the autoassignement be used as pin??
    if True == linotp.lib.policy.ignore_autoassignment_pin(user):
        pin = None

    # if found, assign the found token to the user.login
    try:
        assignToken(serial, user, pin)
        c.audit['serial'] = serial
        c.audit['info'] = "Token auto assigned"
        c.audit['token_type'] = token.getType()
        ret = True
    except Exception as e:
        log.error("[auto_assignToken] Failed to assign token: %r" % e)
        return False

    return ret


def assignToken(serial, user, pin, param=None):
    '''
    assignToken - used to assign and to unassign token
    '''
    if param is None:
        param = {}

    log.debug('[assignToken] entering function assignToken()')
    toks = getTokens4UserOrSerial(None, serial)
    #toks  = Session.query(Token).filter(Token.LinOtpTokenSerialnumber == serial)

    if len(toks) > 1:
        log.warning("[assignToken] multiple tokens found with serial: %r" % serial)
        raise TokenAdminError("multiple tokens found!", id=1101)
    if len(toks) == 0:
        log.warning("[assignToken] no tokens found with serial: %r" % serial)
        raise TokenAdminError("no token found!", id=1102)

    token = toks[0]
    if (user.login == ""):
        report = False
    else:
        report = True

    token.setUser(user, report)

    ## set the Realms of the Token
    realms = getRealms4Token(user)
    token.setRealms(realms)

    if pin is not None:
        token.setPin(pin, param)

    ## reset the OtpCounter
    token.setFailCount(0)

    try:
        token.storeToken()
    except Exception as e:
        log.error('[assign Token] update Token DB failed')
        raise TokenAdminError("Token assign failed for %s/%s : %r"
                              % (user.login, serial, e), id=1105)

    log.debug("[assignToken] successfully assigned token with serial "
              "%r to user %r" % (serial, user.login))
    return True


def unassignToken(serial, user, pin):
    '''
    unassignToken - used to assign and to unassign token
    '''
    log.debug('[unassignToken] entering function unassignToken()')
    toks = getTokens4UserOrSerial(None, serial)
    #toks  = Session.query(Token).filter(Token.LinOtpTokenSerialnumber == serial)

    if len(toks) > 1:
        log.warning("[unassignToken] multiple tokens found with serial: %r" % serial)
        raise TokenAdminError("multiple tokens found!", id=1101)
    if len(toks) == 0:
        log.warning("[unassignToken] no tokens found with serial: %r" % serial)
        raise TokenAdminError("no token found!", id=1102)

    token = toks[0]
    u = User('', '', '')
    token.setUser(u, True)
    token.setPin(pin)

    ## reset the OtpCounter
    token.setFailCount(0)

    try:
        token.storeToken()
    except Exception as e:
        log.error('[unassignToken] update token DB failed')
        raise TokenAdminError("Token assign failed for %r/%r: %r"
                              % (user, serial, e), id=1105)

    log.debug("[unassignToken] successfully unassigned token with serial %r"
               % serial)
    return True


def checkSerialPass(serial, passw, options=None, user=None):
    '''
    This function checks the otp for a given serial
    @attention: the parameter user must be set, as the pin policy==1 will verify the user pin
    '''

    log.debug("[checkSerialPass] checking for serial %r"
              % (serial))
    tokenList = getTokens4UserOrSerial(None, serial, forUpdate=True)

    if passw is None:
        ## other than zero or one token should not happen, as serial is unique
        if len(tokenList) == 1:
            theToken = tokenList[0]
            tok = theToken.token
            realms = tok.getRealmNames()
            if realms is None or len(realms) == 0:
                realm = getDefaultRealm()
            elif len(realms) > 0:
                realm = realms[0]
            userInfo = getUserInfo(tok.LinOtpUserid, tok.LinOtpIdResolver, tok.LinOtpIdResClass)
            user = User(login=userInfo.get('username'), realm=realm)

            if theToken.is_challenge_request(passw, user, options=options):
                (res, opt) = linotp.lib.validate.create_challenge(tokenList[0], options)
            else:
                raise ParameterError("Missing parameter: pass", id=905)

        else:
            raise Exception('No token found: unable to create challenge for %s' % serial)

    else:
        log.debug("[checkSerialPass] checking len(pass)=%r for serial %r"
              % (len(passw), serial))

        (res, opt) = checkTokenList(tokenList, passw, user=user, options=options)

    return (res, opt)

def checkYubikeyPass(passw):
    '''
    Checks the password of a yubikey in Yubico mode (44,48), where the first
    12 or 16 characters are the tokenid

    :param passw: The password that consist of the static yubikey prefix and the otp
    :type passw: string

    :return: True/False and the User-Object of the token owner
    :rtype: dict
    '''
    opt = None
    res = False

    tokenList = []

    # strip the yubico OTP and the PIN
    modhex_serial = passw[:-32][-16:]
    try:
        serialnum = "UBAM" + modhex_decode(modhex_serial)
    except TypeError as exx:
        log.error("Failed to convert serialnumber: %r" % exx)
        return res, opt

    ## build list of possible yubikey tokens
    serials = [serialnum]
    for i in range(1, 3):
        serials.append("%s_%s" % (serialnum, i))

    for serial in serials:
        tokens = getTokens4UserOrSerial(serial=serial)
        tokenList.extend(tokens)

    if len(tokenList) == 0:
        c.audit['action_detail'] = ("The serial %s could not be found!"
                                    % serialnum)
        return res, opt

    ## FIXME if the Token has set a PIN and the User does not want to enter the PIN
    ## for authentication, we need to do something different here...
    ## and avoid PIN checking in __checkToken.
    ## We could pass an "option" to __checkToken.
    (res, opt) = checkTokenList(tokenList, passw)

    # Now we need to get the user
    if res is not False and 'serial' in c.audit:
        serial = c.audit.get('serial', None)
        if serial is not None:
            user = getTokenOwner(serial)
            c.audit['user'] = user.login
            c.audit['realm'] = user.realm
            opt = {}
            opt['user'] = user.login
            opt['realm'] = user.realm

    return res, opt

def checkUserPass(user, passw, options=None):
    '''
    :param user: the to be identified user
    :param passw: the identifiaction pass
    :param options: optional parameters, which are provided
                to the token checkOTP / checkPass

    :return: tuple of True/False and optional information
    '''

    log.debug("[checkUserPass] entering function checkUserPass(%r)" % (user.login))
    # the upper layer will catch / at least should ;-)

    opt = None
    serial = None
    resolverClass = None
    uid = None

    if user is not None and (user.isEmpty() == False):
    # the upper layer will catch / at least should
        try:
            (uid, resolver, resolverClass) = getUserId(user)
        except:
            passOnNoUser = "PassOnUserNotFound"
            passOn = getFromConfig(passOnNoUser, False)
            if False != passOn and "true" == passOn.lower():
                c.audit['action_detail'] = "authenticated by PassOnUserNotFound"
                return (True, opt)
            else:
                c.audit['action_detail'] = "User not found"
                return (False, opt)

    tokenList = getTokens4UserOrSerial(user, serial, forUpdate=True)

    if len(tokenList) == 0:
        c.audit['action_detail'] = "User has no tokens assigned"

        # here we check if we should to autoassign and try to do it
        log.debug("[checkUserPass] about to check auto_assigning")

        auto_assign_return = auto_assignToken(passw, user)
        if auto_assign_return == True:
            # We can not check the token, as the OTP value is already used!
            # But we will authenticate the user....
            return (True, opt)

        passOnNoToken = "PassOnUserNoToken"
        passOn = getFromConfig(passOnNoToken, False)
        if passOn != False and "true" == passOn.lower():
            c.audit['action_detail'] = "authenticated by PassOnUserNoToken"
            return (True, opt)

        ## Check if there is an authentication policy passthru
        from linotp.lib.policy import get_auth_passthru
        if get_auth_passthru(user):
            log.debug("[checkUserPass] user %r has no token. Checking for "
                      "passthru in realm %r" % (user.login, user.realm))
            y = getResolverObject(resolverClass)
            c.audit['action_detail'] = "Authenticated against Resolver"
            if  y.checkPass(uid, passw):
                return (True, opt)

        ## Check if there is an authentication policy passOnNoToken
        from linotp.lib.policy import get_auth_passOnNoToken
        if get_auth_passOnNoToken(user):
            log.info("[checkUserPass] user %r has not token. PassOnNoToken set - authenticated!")
            c.audit['action_detail'] = "Authenticated by passOnNoToken policy"
            return (True, opt)

        return (False, opt)

    if passw is None:
        raise ParameterError(u"Missing parameter:pass", id=905)

    (res, opt) = checkTokenList(tokenList, passw, user, options=options)
    log.debug("[checkUserPass] return of __checkTokenList: %r " % (res,))

    return (res, opt)


def checkTokenList(tokenList, passw, user=User(), options=None):
    '''
    identify a matching token and test, if the token is valid, locked ..
    This function is called by checkSerialPass and checkUserPass to

    :param tokenList: list of identified tokens
    :param passw: the provided passw (mostly pin+otp)
    :param user: the identified use - as class object
    :param option: additonal parameters, which are passed to the token

    :return: tuple of boolean and optional response
    '''
    log.debug("[__checkTokenList] checking tokenlist: %r" % (tokenList))

    res = False
    reply = None

    tokenclasses = config['tokenclasses']

    ## add the user to the options, so that every token
    ## could see the user
    if options:
        options['user'] = user
    else:
        options = { 'user' : user }

    b = getFromConfig("FailCounterIncOnFalsePin", "False")
    b = b.lower()


    ## if there has been one token in challenge mode, we only handle challenges
    challenge_tokens = []
    pinMatchingTokenList = []
    invalidTokenlist = []
    validTokenList = []
    auditList = []

    chall_reply = None

    import linotp.lib.policy
    pin_policies = linotp.lib.policy.get_pin_policies(user) or []

    for token in tokenList:

        audit = {}
        audit['serial'] = token.getSerial()
        audit['token_type'] = token.getType()
        audit['weight'] = 0

        log.debug("[__checkTokenList] Found user with loginId %r: %r:\n"
                   % (token.getUserId(), token.getSerial()))

        ## check if the token is the list of supported tokens
        ## if not skip to the next token in list
        typ = token.getType()
        if not tokenclasses.has_key(typ.lower()):
            log.error('[initToken] typ %r not found in tokenclasses: %r' %
                      (typ, tokenclasses))
            continue

        ## now check if the token is in the same realm as the user
        if user is not None:
            t_realms = token.token.getRealmNames()
            u_realm = user.getRealm()
            if (len(t_realms) > 0 and len(u_realm) > 0 and
                u_realm.lower() not in t_realms) :
                continue

        tok_va = linotp.lib.validate.ValidateToken(token, context=c)
        ## in case of a failure during checking token, we log the error and
        ## continue with the next one
        try:
            (ret, reply) = tok_va.checkToken(passw, user, options=options)
        except Exception as exx:
            log.error("checking token %r failed: %r" % (token, exx))
            ret = -1

        (cToken, pToken, iToken, vToken) = tok_va.get_verification_result()

        ## if we have a challenge, preserve the challenge response
        if len(cToken) > 0:
            challenge_tokens.extend(cToken)
            chall_reply = reply
            audit['action_detail'] = 'challenge created'
            audit['weight'] = 20

        # this means, the resolver password was wrong
        if len(pToken) == 1 and 1 in pin_policies:
            audit['action_detail'] = "wrong user password %r" % (ret)
            audit['weight'] = 10

        elif len(iToken) == 1:  ## this means the pin is wrong
            ## check, if we should increment
            # do not overwrite other error details!
            audit['action_detail'] = "wrong otp pin %r" % (ret)
            audit['weight'] = 15

            if b == "true":
                # We do not have a complete list of all invalid tokens, if
                # FailCounterIncOnFalsePin is False!
                # So we need the auditList!
                invalidTokenlist.extend(iToken)

        elif len(pToken) == 1 :  ## pin matches but the otp is wrong
            pinMatchingTokenList.extend(pToken)
            audit['action_detail'] = "wrong otp value"
            audit['weight'] = 25

        #any valid otp increments, independend of the tokens state !!
        elif len(vToken) > 0:
            audit['weight'] = 30
            matchinCounter = ret

            #any valid otp increments, independend of the tokens state !!
            token.incOtpCounter(matchinCounter)

            if (token.isActive() == True):
                if token.getFailCount() < token.getMaxFailCount():
                    if token.check_auth_counter():
                        if token.check_validity_period():
                            token.inc_count_auth()
                            token.inc_count_auth_success()
                            validTokenList.extend(vToken)
                        else:
                            audit['action_detail'] = "validity period mismatch"
                    else:
                        audit['action_detail'] = "Authentication counter exceeded"
                else:
                    audit['action_detail'] = "Failcounter exceeded"
            else:
                audit['action_detail'] = "Token inactive"

        # add the audit information to the auditList
        auditList.append(audit)

    # compose one audit entry from all token audit information
    if len(auditList) > 0:
        # sort the list for the value of the key "weight"
        sortedAuditList = sorted(auditList, key=lambda audit_entry: audit_entry.get("weight", 0))
        highest_audit = sortedAuditList[-1]
        c.audit['action_detail'] = highest_audit.get('action_detail', '')
        # check how many highest_audit values entries exist!
        highest_list = filter(lambda audit_entry: audit_entry.get("weight", 0) == highest_audit.get("weight", 0), sortedAuditList)
        if len(highest_list) == 1:
            c.audit['serial'] = highest_audit.get('serial', '')
            c.audit['token_type'] = highest_audit.get('token_type', '')
        else:
            # multiple tokens that might contain "wrong otp value" or "wrong otp pin"
            c.audit['serial'] = ''
            c.audit['token_type'] = ''

    ## handle the processing of challenge tokens
    if len(challenge_tokens) == 1:
        challenge_token = challenge_tokens[0]
        (_res, reply) = linotp.lib.validate.create_challenge(challenge_token, options=options)
        return (False, reply)

    elif len(challenge_tokens) > 1:
        raise Exception("processing of multiple challenges is not supported!")


    log.debug("[checkTokenList] Number of valid tokens found "
              "(validTokenNum): %d" % len(validTokenList))

    res = finish_check_TokenList(validTokenList, pinMatchingTokenList,
                                 invalidTokenlist, user)

    return (res, reply)


def finish_check_TokenList(validTokenList, pinMatchingTokenList,
                                    invalidTokenlist, user):

    validTokenNum = len(validTokenList)


    if validTokenNum > 1:
        c.audit['action_detail'] = "Multiple token found!"
        if user:
            log.error("[__checkTokenList] multiple token match error: "
                      "Several Tokens matching with the same OTP PIN and OTP "
                      "for user %r. Not sure how to authenticate", user.login)
        raise UserError("multiple token match error", id= -33)
        ##return jsonError(-36,"multiple token match error",0)

    elif validTokenNum == 1:
        token = validTokenList[0]

        if user:
            log.info("[__checkTokenList] user %r@%r successfully authenticated."
                      % (user.login, user.realm))
        else:
            log.info("[__checkTokenList] serial %r successfully authenticated."
                      % c.audit.get('serial'))
        token.statusValidationSuccess()
        return True


    elif validTokenNum == 0:
        if user:
            log.warning("[__checkTokenList] user %r@%r failed to authenticate."
                        % (user.login, user.realm))
        else:
            log.warning("[__checkTokenList] serial %r failed to authenticate."
                        % c.audit.get('serial'))
        pinMatching = False;

        # check, if there have been some tokens
        # where the pin matched (but OTP failed
        # and increment only these
        for tok in pinMatchingTokenList:
            tok.incOtpFailCounter()
            tok.statusValidationFail()
            tok.inc_count_auth()
            pinMatching = True

        if pinMatching == False:
            for tok in invalidTokenlist:
                tok.incOtpFailCounter()
                tok.statusValidationFail()

    return False

def get_multi_otp(serial, count=0, epoch_start=0, epoch_end=0, curTime=None):
    '''
    This function returns a list of OTP values for the given Token.
    Please note, that this controller needs to be activated and
    that the tokentype needs to support this function.

    method
        get_multi_otp    - get the list of OTP values

    parameter
        serial            - the serial number of the token
        count             - number of the <count> next otp values (to be used with event or timebased tokens)
        epoch_start       - unix time start date (used with timebased tokens)
        epoch_end         - unix time end date (used with timebased tokens)
        curTime          - used for selftest

    return
        dictionary of otp values
    '''
    ret = {"result" : False}
    log.debug("[get_multi_otp] retrieving OTP values for token %r" % serial)
    toks = getTokens4UserOrSerial(None, serial)
    if len(toks) > 1:
        log.error("[get_multi_otp] multiple tokens with serial %r found - cannot get OTP!" % serial)
        raise TokenAdminError("multiple tokens found - cannot get OTP!", id=1201)

    if len(toks) == 0:
        log.warning("[getOTP] there is no token with serial %r" % serial)
        ret["error"] = "No Token with serial %s found." % serial

    if len(toks) == 1:
        token = toks[0]
        log.debug("[get_multi_otp] getting multiple otp values for token %r. curTime=%r" % (token, curTime))
        # if the token does not support getting the OTP value, res==False is returned
        (res, error, otp_dict) = token.get_multi_otp(count=count, epoch_start=epoch_start, epoch_end=epoch_end, curTime=curTime)
        log.debug("[get_multi_otp] received %r, %r, %r" % (res, error, otp_dict))

        if res == True:
            ret = otp_dict
            ret["result"] = True
        else:
            ret["error"] = error

    return ret

def getOtp(serial, curTime=None):
    '''
    This function returns the current OTP value for a given Token.
    Please note, that this controller needs to be activated and
    that the tokentype needs to support this function.

    method
        getOtp    - get the current OTP value

    parameter
        serial    - serialnumber for token
        curTime   - used for self test

    return
        tuple with (res, pin, otpval, passw)

    '''
    log.debug("[getOtp] retrieving OTP value for token %r" % serial)
    toks = getTokens4UserOrSerial(None, serial)

    if len(toks) > 1:
        raise TokenAdminError("multiple tokens found - cannot get OTP!", id=1101)

    if len(toks) == 0:
        log.warning("[getOTP] there is no token with serial %r" % serial)
        return (-1, "", "", "")

    if len(toks) == 1:
        token = toks[0]
        # if the token does not support getting the OTP value, a -2 is returned.
        return token.getOtp(curTime=curTime)


def get_token_by_otp(token_list=None, otp="", window=10, typ=u"HMAC", realm=None, assigned=None):
    '''
    method
        get_token_by_otp    - from the given token list this function returns
                              the token, that generates the given OTP value
    :param token_list:        - the list of token objects to be investigated
    :param otpval:            - the otp value, that needs to be found
    :param window:            - the window of search
    :param assigned:          - or unassigned tokens (1/0)

    :return:         returns the token object.
    '''
    result_token = None

    resultList = []
    log.debug("[get_token_by_otp] entering function. Searching for otp=%r" % otp)

    if token_list is None:
        token_list = getTokensOfType(typ, realm, assigned)

    for token in token_list:
        log.debug("[get_token_by_otp] checking token %r" % token.getSerial())
        r = token.check_otp_exist(otp=otp, window=window)
        log.debug("[get_token_by_otp] result = %d" % int(r))
        if r >= 0:
            resultList.append(token)

    if len(resultList) == 1:
        result_token = resultList[0]
    elif len(resultList) > 1:
        raise TokenAdminError("get_token_by_otp: multiple tokens are matching this OTP value!", id=1200)

    return result_token

def get_serial_by_otp(token_list=None, otp="", window=10, typ=None, realm=None, assigned=None):
    '''
    Returns the serial for a given OTP value and the user
    (serial, user)

    :param otp:      -  the otp value to be searched
    :param window:   -  how many OTPs should be calculated per token
    :param typ:      -  The tokentype
    :param realm:    -  The realm in which to search for the token
    :param assigned: -  search either in assigned (1) or not assigend (0) tokens

    :return: the serial for a given OTP value and the user
    '''
    serial = ""
    username = ""
    resolverClass = ""

    token = get_token_by_otp(token_list, otp, window, typ, realm, assigned)

    if token is not None:
        serial = token.getSerial()
        uid, resolver, resolverClass = token.getUser()
        userInfo = getUserInfo(uid, resolver, resolverClass)
        log.debug("[get_serial_by_otp] userinfo for token: %r" % userInfo)
        username = userInfo.get("username", "")

    return serial, username, resolverClass

def removeToken(user=None, serial=None):

    if (user is None or user.isEmpty() == True) and (serial is None):
        log.warning("[removeToken] Parameter user or serial required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[removeToken] for serial: %r, user: %r" % (serial, user))
    tokenList = getTokens4UserOrSerial(user, serial,
                                       forUpdate=True, _class=False)

    serials = []
    tokens = []
    token_ids = []
    try:

        for token in tokenList:
            ser = token.getSerial()
            serials.append(ser)
            token_ids.append(token.LinOtpTokenId)
            tokens.append(token)

        ## we cleanup the challenges
        challenges = set()
        for serial in serials:
            serial = linotp.lib.crypt.uencode(serial)
            challenges.update(linotp.lib.validate.get_challenges(serial=serial))

        for chall in challenges:
            Session.delete(chall)

        ## due to legacy SQLAlchemy it could happen that the
        ## foreign key relation could not be deleted
        ## so we do this manualy

        for t_id in token_ids:
            Session.query(TokenRealm).filter(TokenRealm.token_id == t_id).delete()

        Session.commit()

        for token in tokens:
            Session.delete(token)


    except Exception as e:
        log.error('[removeToken] update token DB failed')
        raise TokenAdminError("removeToken: Token update failed: %r" % e, id=1132)


    return len(tokenList)


def setMaxFailCount(maxFail, user, serial):

    if (user is None) and (serial is None):
        log.warning("[setMaxFailCount] Parameter user or serial required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[setMaxFailCount] for serial: %r, user: %r" % (serial, user))
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setMaxFail(maxFail)

    return len(tokenList)

def enableToken(enable, user, serial):

    if (user is None) and (serial is None):
        log.warning("[enableToken] parameter serial or user missing.")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[enableToken] enable=%r, user=%r, serial=%r" % (enable, user, serial))
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.enable(enable)

    return len(tokenList)

def copyTokenPin(serial_from, serial_to):
    '''
    This function copies the token PIN from one token to the other token.
    This can be used for workflows like lost token.

    In fact the PinHash and the PinSeed need to be transferred

    returns:
        1 : success
        -1: no source token
        -2: no destination token
    '''
    log.debug("[copyTokenPin] copying PIN from token %r to token %r" % (serial_from, serial_to))
    tokens_from = getTokens4UserOrSerial(None, serial_from)
    tokens_to = getTokens4UserOrSerial(None, serial_to)
    if len(tokens_from) != 1:
        log.error("[copyTokenPin] not a unique token to copy from found")
        return -1
    if len(tokens_to) != 1:
        log.error("[copyTokenPin] not a unique token to copy to found")
        return -2
    pinhash, seed = tokens_from[0].getPinHashSeed()
    tokens_to[0].setPinHashSeed(pinhash, seed)
    return 1

def copyTokenUser(serial_from, serial_to):
    '''
    This function copies the user from one token to the other
    This can be used for workflows like lost token

    returns:
        1: success
        -1: no source token
        -2: no destination token
    '''
    log.debug("[copyTokenUser] copying user from token %r to token %r" % (serial_from, serial_to))
    tokens_from = getTokens4UserOrSerial(None, serial_from)
    tokens_to = getTokens4UserOrSerial(None, serial_to)
    if len(tokens_from) != 1:
        log.error("[copyTokenUser] not a unique token to copy from found")
        return -1
    if len(tokens_to) != 1:
        log.error("[copyTokenUser] not a unique token to copy to found")
        return -2
    uid, ures, resclass = tokens_from[0].getUser()
    tokens_to[0].setUid(uid, ures, resclass)

    copyTokenRealms(serial_from, serial_to)
    return 1

def copyTokenRealms(serial_from, serial_to):
    realmlist = getTokenRealms(serial_from)
    setRealms(serial_to, realmlist)

def losttoken(serial, new_serial="", password="", default_validity=0):
    """
    This is the workflow to handle a lost token

    :param serial: Token serial number
    :param new_serial: new serial number
    :param password: new password
    :param default_validity: set the token to be valid

    :return: result dictionary
    """

    res = {}
    if new_serial == "":
        new_serial = "lost%s" % serial

    user = getTokenOwner(serial)
    log.error("[losttoken] doing lost token for serial %r and user %r@%r"
                                            % (serial, user.login, user.realm))

    if user.login == "" or user.login is None:
        err = "You can only define a lost token for an assigned token."
        log.warning("[losttoken] %s" % err)
        raise Exception(err)

    pol = linotp.lib.policy.get_client_policy(get_client(),
                                    scope="enrollment", realm=user.realm,
                                    user=user.login, userObj=user)

    pw_len = linotp.lib.policy.getPolicyActionValue(pol, "lostTokenPWLen")
    validity = linotp.lib.policy.getPolicyActionValue(pol, "lostTokenValid",
                                                      max=False)
    contents = linotp.lib.policy.getPolicyActionValue(pol,
                                            "lostTokenPWContents", String=True)

    log.debug("losttoken: length: %r, "
              "validity: %r, contents: %r" % (pw_len, validity, contents))

    if validity == -1:
        validity = 10
    if 0 != default_validity:
        validity = default_validity

    if pw_len == -1:
        pw_len = 10

    character_pool = "%s%s%s" % (string.ascii_lowercase,
                                 string.ascii_uppercase, string.digits)
    if contents != "":
        character_pool = ""
        if "c" in contents:
            character_pool += string.ascii_lowercase
        if "C" in contents:
            character_pool += string.ascii_uppercase
        if "n" in contents:
            character_pool += string.digits
        if "s" in contents:
            character_pool += "!#$%&()*+,-./:;<=>?@[]^_"

    if password == "":
        password = generate_password(size=pw_len, characters=character_pool)

    res['serial'] = new_serial

    (ret, tokenObj) = initToken({ "otpkey" : password,
                        "serial" : new_serial,
                        "type" : "pw",
                        "description" : "temporary replacement for %s" % serial
                         }, User('', '', ''))
    res['init'] = ret
    if True == ret:
        res['user' ] = copyTokenUser(serial, new_serial)
        res['pin'] = copyTokenPin(serial, new_serial)

        # set validity period
        end_date = (datetime.date.today()
                    + datetime.timedelta(days=validity)).strftime("%d/%m/%y")

        end_date = "%s 23:59" % end_date
        tokens = getTokens4UserOrSerial(User('', '', ''), new_serial)
        for tok in tokens:
            tok.set_validity_period_end(end_date)

        # fill results
        res['valid_to'] = "xxxx"
        res['password'] = password
        res['end_date'] = end_date
        # disable token
        res['disable'] = enableToken(False, User('', '', ''), serial)

    return res


def setPin(pin, user, serial, param=None):
    '''
    set the PIN
    '''
    if param is None:
        param = {}

    log.debug("[setPin] calling setPin.")

    if (user is None) and (serial is None):
        log.warning("[setPin] Parameter user or serial required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    if (user is not None):
        log.info("[setPin] setting Pin for user %r@%r" % (user.login, user.realm))
    if (serial is not None):
        log.info("[setPin] setting Pin for token with serial %r" % serial)

    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setPin(pin, param)

    return len(tokenList)

def setOtpLen(otplen, user, serial):

    if (user is None) and (serial is None):
        log.warning("[setOtpLen] Parameter user or serial required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    if (serial is not None):
        log.debug("[setOtpLen] setting OTP length for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setOtpLen(otplen)

    return len(tokenList)

def setHashLib(hashlib, user, serial):
    '''
    sets the Hashlib in the tokeninfo
    '''
    if user is None and serial is None:
        log.warning("[setHashLib] Parameter user or serial required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    if serial is not None:
        log.debug("[setHashLib] setting hashlib for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setHashLib(hashlib)

    return len(tokenList)

def setCountAuth(count, user, serial, max=False, success=False):
    '''
    sets either of the counters:
        count_auth
        count_auth_max
        count_auth_success
        count_auth_success_max
    '''
    if user is None and serial is None:
        log.warning("[setCountAuth] Parameter user or serial required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    if serial is not None:
        log.debug("[setCountAuth] setting authcount for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        if max:
            if success:
                token.set_count_auth_success_max(count)
            else:
                token.set_count_auth_max(count)
        else:
            if success:
                token.set_count_auth_success(count)
            else:
                token.set_count_auth(count)

    return len(tokenList)


def addTokenInfo(info, value, user, serial):
    '''
    sets an abitrary Tokeninfo field
    '''
    if user is None and serial is None:
        log.warning("[setTokenInfo] Parameter user or serial required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    if serial is not None:
        log.debug("[setTokenInfo] setting tokeninfo %r for serial %r" % (info, serial))
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.addToTokenInfo(info, value)

    return len(tokenList)

###############################################################################
## LinOtpTokenPinUser
###############################################################################
def setPinUser(userPin, serial):

    user = None

    if serial is None:
        log.warning("[setPinUser] Parameter serial required!")
        raise ParameterError("Parameter 'serial' is required!", id=1212)

    log.debug("[setPin] setting Pin for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setUserPin(userPin)

    return len(tokenList)

###############################################################################
## LinOtpTokenPinSO
###############################################################################
def setPinSo(soPin, serial):
    user = None

    if serial is None:
        log.warning("[setPinSo] Parameter serial required!")
        raise ParameterError("Parameter 'serial' is required!", id=1212)

    log.debug("[setPinSo] setting Pin for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setSoPin(soPin)

    return len(tokenList)

def setSyncWindow(syncWindow, user, serial):

    if user is None and serial is None:
        log.warning("[setSyncWindow] Parameter serial or user required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[setSyncWindow] setting syncwindow for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setSyncWindow(syncWindow)

    return len(tokenList)

def setCounterWindow(countWindow, user, serial):

    if user is None and serial is None:
        log.warning("[setCounterWindow] Parameter serial or user required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[setCounterWindow] setting count window for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setCounterWindow(countWindow)

    return len(tokenList)

def setDescription(description, user, serial):

    if user is None and serial is None:
        log.warning("[setDescription] Parameter serial or user required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[setDescription] setting count window for serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.setDescription(description)

    return len(tokenList)

def resyncToken(otp1, otp2, user, serial, options=None):
    ret = False

    if (user is None) and (serial is None):
        log.warning("[resyncToken] Parameter serial or user required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[resyncToken] resync token with serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        res = token.resync(otp1, otp2, options)
        if res == True:
            ret = True
    return ret

def resetToken(user=None, serial=None):

    if (user is None) and (serial is None):
        log.warning("[resetToken] Parameter serial or user required!")
        raise ParameterError("Parameter user or serial required!", id=1212)

    log.debug("[resetToken] reset token with serial %r" % serial)
    tokenList = getTokens4UserOrSerial(user, serial)

    for token in tokenList:
        token.addToSession(Session)
        token.reset()

    return len(tokenList)


def _gen_serial(prefix, tokennum, min_len=8):
    '''
    helper to create a hex digit string

    :param prefix: the prepended prefix like LSGO
    :param tokennum: the token number counter (int)
    :param min_len: int, defining the length of the hex string
    :return: hex digit string
    '''
    h_serial = ''
    num_str = '%.4d' % tokennum
    h_len = min_len - len(num_str)
    if h_len > 0:
        h_serial = binascii.hexlify(os.urandom(h_len)).upper()[0:h_len]
    return "%s%s%s" % (prefix, num_str, h_serial)


def genSerial(tokenType=None, prefix=None):
    '''
    generate a serial number similar to the one generated in the manage web gui

    :param tokenType: the token type prefix is done by a lookup on the tokens
    :return: serial number
    '''
    if tokenType is None:
        tokenType = 'LSUN'

    tokenprefixes = config['tokenprefixes']

    if prefix is None:
        prefix = tokenType.upper()
        if tokenType.lower() in tokenprefixes:
            prefix = tokenprefixes.get(tokenType.lower())

    ## now search the number of ttypes in the token database
    tokennum = Session.query(Token).filter(
                    Token.LinOtpTokenType == u'' + tokenType).count()

    serial = _gen_serial(prefix, tokennum + 1)

    ## now test if serial already exists
    while True:
        numtokens = Session.query(Token).filter(
                        Token.LinOtpTokenSerialnumber == u'' + serial).count()
        if numtokens == 0:
            ## ok, there is no such token, so we're done
            break
        ## else - rare case:
        ## we add the numtokens to the number of existing tokens with serial
        serial = _gen_serial(prefix, tokennum + numtokens)

    return serial

def getTokenConfig(tok, section=None):
    '''
    getTokenConfig - return the config definition
                     of a dynamic token

    :param tok: token type (shortname)
    :type  tok: string

    :param section: subsection of the token definition - optional
    :type   section: string

    :return: dict - if nothing found an empty dict
    :rtype:  dict
    '''
    res = {}

    g = config['pylons.app_globals']
    tokenclasses = g.tokenclasses

    if tok in tokenclasses.keys():
        tclass = tokenclasses.get(tok)
        tclt = newToken(tclass)
        # check if we have a policy in the token definition
        if hasattr(tclt, 'getClassInfo'):
            res = tclt.getClassInfo(section, ret={})

    return res


### TODO: move TokenIterator to dedicated file

class TokenIterator(object):
    '''
    TokenIterator class - support a smooth iterating through the tokens
    '''

    def __init__(self, user, serial, page=None, psize=None, filter=None,
                 sort=None, sortdir=None, filterRealm=None, user_fields=None,
                 params=None):
        '''
        constructor of Tokeniterator, which gathers all conditions to build
        a sqalchemy query - iterator

        :param user:     User object - user provides as well the searchfield entry
        :type  user:     User class
        :param serial:   serial number of a token
        :type  serial:   string
        :param page:     page number
        :type  page:     int
        :param psize:    how many entries per page
        :type  psize:    int
        :param filter:   additional condition
        :type  filter:   string
        :param sort:     sort field definition
        :type  sort:     string
        :param sortdir:  sort direction: ascending or descending
        :type  sortdir:  string
        :param filterRealm:  restrict the set of token to those in the filterRealm
        :type  filterRealm:  string or list
        :param user_fields:  list of additional fields from the user owner
        :type  user_fields: array
        :param params:  list of additional request parameters - currently not used
        :type  params: dict

        :return: - nothing / None

        '''
        log.debug('[TokenIterator::init] begin. start creating TokenIterator \
        class with parameters: user:%r, serial:%r, page=%r, psize:%r, \
                    filter:%r, sort:%r, sortdir:%r, filterRealm:%r' %
                (user, serial, page, psize, filter, sort, sortdir, filterRealm))

        if params is None:
            params = {}


        self.page = 1
        self.pages = 1
        self.tokens = 0
        self.user_fields = user_fields
        if self.user_fields == None:
            self.user_fields = []

        condition = None
        ucondition = None
        scondition = None
        r_condition = None

        if type(filterRealm) in (str, unicode):
            filterRealm = filterRealm.split(',')

        if type(filterRealm) in [list]:
            s_realms = []
            for f in filterRealm:
                ## support for multiple realm filtering in the ui
                ## as a coma separated string
                for s_realm in f.split(','):
                    s_realms.append(s_realm.strip())
            filterRealm = s_realms

        ## create a list of all realms, which are allowed to be searched
        ## based on the list of the existing ones
        valid_realms = []
        realms = getRealms().keys()
        if '*' in filterRealm:
            valid_realms.append("*")
        else:
            for realm in realms:
                if realm in filterRealm:
                    realm = linotp.lib.crypt.uencode(realm)
                    valid_realms.append(realm)


        if serial is not None:
            ## check if the requested serial is in the realms of the admin (filterRealm)
            log.debug('[TokenIterator::init] start search for serial: >%r<' % (serial))

            allowed = False
            if filterRealm == ['*']:
                allowed = True
            else:
                realms = getTokenRealms(serial)
                for realm in realms:
                    if realm in filterRealm:
                        allowed = True

            if allowed == True:
                scondition = and_(Token.LinOtpTokenSerialnumber == serial)

        if user.isEmpty() == False and user is not None:
            log.debug('[TokenIterator::init] start search for username: >%r<'
                      % (user))

            if user.login is not None and (user.login) > 0 :
                loginUser = user.login.lower()
                loginUser = loginUser.replace('"', '')
                loginUser = loginUser.replace("'", '')

                searchType = "any"

                ## search for a 'blank' user
                if len(loginUser) == 0 and len(user.login) > 0:
                    searchType = "blank"
                elif loginUser == "/:no user:/" or loginUser == "/:none:/":
                    searchType = "blank"
                elif loginUser == "/:no user info:/":
                    searchType = "wildcard"
                elif "*" in loginUser or "." in loginUser:
                    searchType = "wildcard"
                else:
                    ## no blank and no wildcard search
                    searchType = "exact"

                if searchType == "blank":
                    log.debug('[TokenIterator::init] search for empty user: >%r<' % (user.login))
                    ucondition = and_(or_(Token.LinOtpUserid == u'',
                                          Token.LinOtpUserid == None))

                if searchType == "exact":
                    log.debug('[TokenIterator::init] search for exact user: %r' % (user))
                    serials = []
                    users = []

                    ## if search for a realmuser 'user@realm' we can take the
                    ## realm from the argument
                    if len(user.realm) > 0:
                        users.append(user)
                    else:
                        for realm in valid_realms:
                            users.append(User(user.login, realm))

                    # resolve the realm with wildcard:
                    # identify all users and add these to the userlist
                    userlist = []
                    for usr in users:
                        urealm =  usr.realm
                        if urealm == '*':
                            # if the realm is set to *, the getUserId
                            # triggers the identification of all resolvers, where the
                            # user might reside: tigger the user resolver lookup
                            (uid, resolver, resolverClass) = getUserId(usr)
                            userlist.extend(usr.getUserPerConf())
                        else:
                            userlist.append(usr)

                    for usr in userlist:
                        try:
                            tokens = getTokens4UserOrSerial(user=usr, _class=False)
                            for tok in tokens:
                                serials.append(tok.LinOtpTokenSerialnumber)
                        except UserError as ex:
                            ## we get an exception if the user is not found
                            log.debug('[TokenIterator::init] no exact user: %r'
                                      % (user))
                            log.debug('[TokenIterator::init] %r' % ex)

                    if len(serials) > 0:
                        ## if tokens found, search for their serials
                        ucondition = and_(Token.LinOtpTokenSerialnumber.in_(serials))
                    else:
                        ## if no token is found, block search for user
                        ## and return nothing
                        ucondition = and_(or_(Token.LinOtpUserid == u'',
                                              Token.LinOtpUserid == None))

                ## handle case, when nothing found in former cases
                if searchType == "wildcard":
                    log.debug('[TokenIterator::init] wildcard search: %r' % (user))
                    serials = []
                    users = getAllTokenUsers()
                    logRe = None
                    lU = loginUser.replace('*', '.*')
                    #lU = lU.replace('..', '.')
                    logRe = re.compile(lU)

                    for ser in users:
                        userInfo = users.get(ser)
                        tokenUser = userInfo.get('username').lower()
                        try:
                            if logRe.match(u'' + tokenUser) is not None:
                                serials.append(ser)
                        except Exception as e:
                            log.error('error no express %r ' % e)

                    ## to prevent warning, we check is serials are found
                    ## SAWarning: The IN-predicate on
                    ## "Token.LinOtpTokenSerialnumber" was invoked with an
                    ## empty sequence. This results in a contradiction, which
                    ## nonetheless can be expensive to evaluate.  Consider
                    ## alternative strategies for improved performance.
                    if len(serials) > 0:
                        ucondition = and_(Token.LinOtpTokenSerialnumber.in_(serials))
                    else:
                        ucondition = and_(or_(Token.LinOtpUserid == u'',
                                              Token.LinOtpUserid == None))

        if filter is None:
            condition = None
        elif filter in ['/:active:/', '/:enabled:/',
                        '/:token is active:/', '/:token is enabled:/' ]:
            condition = and_(Token.LinOtpIsactive == True)
        elif filter in ['/:inactive:/', '/:disabled:/',
                        '/:token is inactive:/', '/:token is disabled:/']:
            condition = and_(Token.LinOtpIsactive == False)
        else:
            ## search in other colums
            filter = linotp.lib.crypt.uencode(filter)
            condition = or_(Token.LinOtpTokenDesc.contains(filter),
                            Token.LinOtpIdResClass.contains(filter),
                            Token.LinOtpTokenSerialnumber.contains(filter),
                            Token.LinOtpUserid.contains(filter),
                            Token.LinOtpTokenType.contains(filter))

        ###################################################################
        ##  The condition for only getting certain realms!
        if '*' in valid_realms:
            log.debug("[TokenIterator::init] wildcard for realm '*' found."
                      " Tokens of all realms will be displayed")
        elif len(valid_realms) > 0:
            log.debug("[TokenIterator::init] adding filter condition"
                      " for realm %r" % valid_realms)

            ## get all matching realms
            realm_id_tuples = Session.query(Realm.id).\
                                filter(Realm.name.in_(valid_realms)).all()
            realm_ids = set()
            for realm_tuple in realm_id_tuples:
                realm_ids.add(realm_tuple[0])
            ## get all tokenrealm ids
            token_id_tuples = Session.query(TokenRealm.token_id).\
                        filter(TokenRealm.realm_id.in_(realm_ids)).all()
            token_ids = set()
            for token_tuple in token_id_tuples:
                token_ids.add(token_tuple[0])

            ## define the token id condition
            r_condition = and_(Token.LinOtpTokenId.in_(token_ids))

        elif ("''" in filterRealm or '""' in filterRealm or
              "/:no realm:/" in filterRealm):
            log.debug("[TokenIterator::init] search for all tokens, which are"
                      " in no realm")

            ## get all tokenrealm ids
            token_id_tuples = Session.query(TokenRealm.token_id).all()
            token_ids = set()
            for token_tuple in token_id_tuples:
                token_ids.add(token_tuple[0])

            ## define the token id not condition
            r_condition = and_(not_(Token.LinOtpTokenId.in_(token_ids)))


        ## create the final condition as AND of all conditions
        condTuple = ()
        for conn in (condition, ucondition, scondition, r_condition):
            if type(conn).__name__ != 'NoneType':
                condTuple += (conn,)

        condition = and_(*condTuple)

        order = Token.LinOtpTokenDesc

        ##  o LinOtp.TokenId: 17943
        ##  o LinOtp.TokenInfo: ""
        ##  o LinOtp.TokenType: "spass"
        ##  o LinOtp.TokenSerialnumber: "spass0000FBA3"
        ##  o User.description: "Cornelius Koelbel,cornelius.koelbel@lsexperts.de,local,"
        ##  o LinOtp.IdResClass: "useridresolver.PasswdIdResolver.IdResolver._default_Passwd_"
        ##  o User.username: "koelbel"
        ##  o LinOtp.TokenDesc: "Always Authenticate"
        ##  o User.userid: "1000"
        ##  o LinOtp.IdResolver: "/etc/passwd"
        ##  o LinOtp.Isactive: true

        if sort == "TokenDesc":
            order = Token.LinOtpTokenDesc
        elif sort == "TokenId":
            order = Token.LinOtpTokenId
        elif sort == "TokenType":
            order = Token.LinOtpTokenType
        elif sort == "TokenSerialnumber":
            order = Token.LinOtpTokenSerialnumber
        elif sort == "TokenType":
            order = Token.LinOtpTokenType
        elif sort == "IdResClass":
            order = Token.LinOtpIdResClass
        elif sort == "IdResolver":
            order = Token.LinOtpIdResolver
        elif sort == "Userid":
            order = Token.LinOtpUserid
        elif sort == "FailCount":
            order = Token.LinOtpFailCount
        elif sort == "Userid":
            order = Token.LinOtpUserid
        elif sort == "Isactive":
            order = Token.LinOtpIsactive

        ## care for the result sort order
        if sortdir is not None and sortdir == "desc":
            order = order.desc()
        else:
            order = order.asc()

        ## care for the result pageing
        if page is None:
            self.toks = Session.query(Token).filter(condition).order_by(order).distinct()
            self.tokens = self.toks.count()

            log.debug("[TokenIterator] DB-Query returned # of objects: %i" % self.tokens)
            self.pagesize = self.tokens
            self.it = iter(self.toks)
            return

        try:
            if psize is None:
                pagesize = int(getFromConfig("pagesize", 50))
            else:
                pagesize = int(psize)
        except:
            pagesize = 20

        try:
            thePage = int (page) - 1
        except:
            thePage = 0
        if thePage < 0:
            thePage = 0

        start = thePage * pagesize
        stop = (thePage + 1) * pagesize

        self.toks = Session.query(Token).filter(condition).order_by(order).distinct()
        self.tokens = self.toks.count()
        log.debug("[TokenIterator::init] DB-Query returned # of objects: %i" % self.tokens)
        self.page = thePage + 1
        fpages = float(self.tokens) / float(pagesize)
        self.pages = int(fpages)
        if fpages - int(fpages) > 0:
            self.pages = self.pages + 1
        self.pagesize = pagesize
        self.toks = self.toks.slice(start, stop)

        self.it = iter(self.toks)

        log.debug('[TokenIterator::init] end. Token iterator created: %r' % \
                  (self.it))

        return

    def getResultSetInfo(self):
        resSet = {"pages"   : self.pages,
                  "pagesize" : self.pagesize,
                  "tokens"  : self.tokens,
                  "page"    : self.page}
        return resSet

    def getUserDetail(self, tok):
        userInfo = {}
        uInfo = {}

        userInfo["User.description"] = u''
        userInfo["User.userid"] = u''
        userInfo["User.username"] = u''
        for field in self.user_fields:
            userInfo["User.%s" % field] = u''

        if tok.LinOtpUserid:
            #userInfo["User.description"]    = u'/:no user info:/'
            userInfo["User.userid"] = u'/:no user info:/'
            userInfo["User.username"] = u'/:no user info:/'

            uInfo = getUserInfo(tok.LinOtpUserid, tok.LinOtpIdResolver, tok.LinOtpIdResClass)
            if uInfo is not None and len(uInfo) > 0:
                if uInfo.has_key("description"):
                    description = uInfo.get("description")
                    if isinstance(description, str):
                        userInfo["User.description"] = description.decode(ENCODING)
                    else:
                        userInfo["User.description"] = description

                if uInfo.has_key("userid"):
                    userid = uInfo.get("userid")
                    if isinstance(userid, str):
                        userInfo["User.userid"] = userid.decode(ENCODING)
                    else:
                        userInfo["User.userid"] = userid

                if uInfo.has_key("username"):
                    username = uInfo.get("username")
                    if isinstance(username, str):
                        userInfo["User.username"] = username.decode(ENCODING)
                    else:
                        userInfo["User.username"] = username

                for field in self.user_fields:
                    fieldvalue = uInfo.get(field, "")
                    if isinstance(fieldvalue, str):
                        userInfo["User.%s" % field] = fieldvalue.decode(ENCODING)
                    else:
                        userInfo["User.%s" % field] = fieldvalue

        return (userInfo, uInfo)

    def next(self):
        log.debug("[next] TokenIterator finds next token")

        tok = self.it.next()
        desc = tok.get_vars(save=True)
        ''' add userinfo to token description '''
        (userInfo, ret) = self.getUserDetail(tok)
        desc.update(userInfo)

        return desc

    def __iter__(self):
        log.debug("[__iter__] TokenIterator")
        return self

#eof###########################################################################

