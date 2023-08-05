## $Id: test_authentication.py 10055 2013-04-04 15:12:43Z uli $
##
## Copyright (C) 2011 Uli Fouquet & Henrik Bettermann
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
import grok
import logging
import time
import unittest
from cStringIO import StringIO
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite, clearSite
from zope.interface.verify import verifyClass, verifyObject
from zope.password.testing import setUpPasswordManagers
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from waeup.kofa.testing import FunctionalTestCase, FunctionalLayer
from waeup.kofa.authentication import (
    UserAuthenticatorPlugin, Account, KofaPrincipalInfo, FailedLoginInfo,
    get_principal_role_manager, UsersPlugin,)
from waeup.kofa.interfaces import (
    IUserAccount, IFailedLoginInfo, IKofaPrincipalInfo, IKofaPluggable)

class FakeSite(grok.Site, grok.Container):
    #def getSiteManager(self):
    #    return None
    #    return getGlobalSiteManager()
    pass

class UserAuthenticatorPluginTests(FunctionalTestCase):
    # Must be functional because of various utility lookups and the like

    layer = FunctionalLayer

    def setUp(self):
        super(UserAuthenticatorPluginTests, self).setUp()
        self.getRootFolder()['app'] = FakeSite()
        self.site = self.getRootFolder()['app']
        self.site['users'] = {'bob': Account('bob', 'secret')}
        setSite(self.site)
        return

    def tearDown(self):
        super(UserAuthenticatorPluginTests, self).tearDown()
        clearSite()
        return

    def test_ifaces(self):
        # make sure, interfaces requirements are met
        plugin = UserAuthenticatorPlugin()
        plugin.__parent__ = None # This attribute is required by iface
        self.assertTrue(
            verifyClass(IAuthenticatorPlugin, UserAuthenticatorPlugin))
        self.assertTrue(verifyObject(IAuthenticatorPlugin, plugin))
        return

    def test_authenticate_credentials(self):
        # make sure authentication works as expected
        plugin = UserAuthenticatorPlugin()
        result1 = plugin.authenticateCredentials(
            dict(login='bob', password='secret'))
        result2 = plugin.authenticateCredentials(
            dict(login='bob', password='nonsense'))
        self.assertTrue(isinstance(result1, KofaPrincipalInfo))
        self.assertTrue(result2 is None)
        return

    def test_principal_info(self):
        # make sure we can get a principal info
        plugin = UserAuthenticatorPlugin()
        result1 = plugin.principalInfo('bob')
        result2 = plugin.principalInfo('manfred')
        self.assertTrue(isinstance(result1, KofaPrincipalInfo))
        self.assertTrue(result2 is None)
        return

    def test_get_principal_role_manager(self):
        # make sure we get different role managers for different situations
        prm1 = get_principal_role_manager()
        clearSite(None)
        prm2 = get_principal_role_manager()
        self.assertTrue(IPrincipalRoleManager.providedBy(prm1))
        self.assertTrue(IPrincipalRoleManager.providedBy(prm2))
        self.assertTrue(prm1._context is self.site)
        self.assertTrue(hasattr(prm2, '_context') is False)
        return

    def make_failed_logins(self, num):
        # do `num` failed logins and a valid one afterwards
        del self.site['users']
        self.site['users'] = {'bob': Account('bob', 'secret')}
        plugin = UserAuthenticatorPlugin()
        resultlist = []
        # reset accounts
        for x in range(num):
            resultlist.append(plugin.authenticateCredentials(
                dict(login='bob', password='wrongsecret')))
        resultlist.append(plugin.authenticateCredentials(
            dict(login='bob', password='secret')))
        return resultlist

    def DISABLED_test_failed_logins(self):
        # after three failed logins, an account is blocked
        # XXX: this tests authenticator with time penalty (currently
        # disabled)
        results = []
        succ_principal = KofaPrincipalInfo(
            id='bob',
            title='bob',
            description=None,
            email=None,
            phone=None,
            public_name=None,
            user_type=u'user')
        for x in range(4):
            results.append(self.make_failed_logins(x))
        self.assertEqual(results[2], [None, None, succ_principal])
        # last login was blocked although correctly entered due to
        # time penalty
        self.assertEqual(results[3], [None, None, None, None])
        return

class KofaPrincipalInfoTests(unittest.TestCase):

    def create_info(self):
        return KofaPrincipalInfo(
            id='bob',
            title='bob',
            description=None,
            email=None,
            phone=None,
            public_name=None,
            user_type=u'user')

    def test_iface(self):
        # make sure we implement the promised interfaces
        info = self.create_info()
        verifyClass(IKofaPrincipalInfo, KofaPrincipalInfo)
        verifyObject(IKofaPrincipalInfo, info)
        return

    def test_equality(self):
        # we can test two infos for equality
        info1 = self.create_info()
        info2 = self.create_info()
        self.assertEqual(info1, info2)
        self.assertTrue(info1 == info2)
        info1.id = 'blah'
        self.assertTrue(info1 != info2)
        self.assertTrue((info1 == info2) is False)
        info1.id = 'bob'
        info2.id = 'blah'
        self.assertTrue(info1 != info2)
        self.assertTrue((info1 == info2) is False)
        return

class FailedLoginInfoTests(unittest.TestCase):

    def test_iface(self):
        # make sure we fullfill the promised interfaces
        info1 = FailedLoginInfo()
        info2 = FailedLoginInfo(num=1, last=time.time())
        self.assertTrue(
            verifyClass(IFailedLoginInfo, FailedLoginInfo))
        self.assertTrue(verifyObject(IFailedLoginInfo, info1))
        # make sure the stored values have correct type if not None
        self.assertTrue(verifyObject(IFailedLoginInfo, info2))
        return

    def test_default_values(self):
        # By default we get 0, None
        info = FailedLoginInfo()
        self.assertEqual(info.num, 0)
        self.assertEqual(info.last, None)
        return

    def test_set_values_by_attribute(self):
        # we can set values by attribute
        ts = time.gmtime(0)
        info = FailedLoginInfo()
        info.num = 5
        info.last = ts
        self.assertEqual(info.num, 5)
        self.assertEqual(info.last, ts)
        return

    def test_set_values_by_constructor(self):
        # we can set values by constructor args
        ts = time.gmtime(0)
        info = FailedLoginInfo(5, ts)
        self.assertEqual(info.num, 5)
        self.assertEqual(info.last, ts)
        return

    def test_set_values_by_keywords(self):
        # we can set values by constructor keywords
        ts = time.gmtime(0)
        info = FailedLoginInfo(last=ts, num=3)
        self.assertEqual(info.num, 3)
        self.assertEqual(info.last, ts)
        return

    def test_as_tuple(self):
        # we can get the info values as tuple
        ts = time.gmtime(0)
        info = FailedLoginInfo(last=ts, num=3)
        self.assertEqual(info.as_tuple(), (3, ts))
        return

    def test_set_values(self):
        # we can set the values of a an info instance
        ts = time.time()
        info = FailedLoginInfo()
        info.set_values(num=3, last=ts)
        self.assertEqual(info.num, 3)
        self.assertEqual(info.last, ts)
        return

    def test_increase(self):
        # we can increase the number of failed logins
        ts1 = time.time()
        info = FailedLoginInfo()
        info.increase()
        self.assertEqual(info.num, 1)
        self.assertTrue(info.last > ts1)
        ts2 = info.last
        info.increase()
        self.assertEqual(info.num, 2)
        self.assertTrue(info.last > ts2)
        return

    def test_reset(self):
        # we can reset failed login infos.
        info = FailedLoginInfo()
        info.increase()
        info.reset()
        self.assertEqual(info.num, 0)
        self.assertEqual(info.last, None)
        return

class AccountTests(unittest.TestCase):

    def setUp(self):
        setUpPasswordManagers()
        return

    def test_iface(self):
        acct = Account('bob', 'mypasswd')
        self.assertTrue(
            verifyClass(IUserAccount, Account))
        self.assertTrue(
            verifyObject(IUserAccount, acct))
        return

    def test_failed_logins(self):
        # we can retrieve infos about failed logins
        ts = time.time()
        acct = Account('bob', 'mypasswd')
        self.assertTrue(hasattr(acct, 'failed_logins'))
        acct.failed_logins.set_values(num=3, last=ts)
        self.assertEqual(acct.failed_logins.last, ts)
        self.assertEqual(acct.failed_logins.num, 3)
        return

    def test_failed_logins_per_inst(self):
        # we get a different counter for each Account instance
        acct1 = Account('bob', 'secret')
        acct2 = Account('alice', 'alsosecret')
        self.assertTrue(acct1.failed_logins is not acct2.failed_logins)
        return

class FakeUserAccount(object):
    pass

class UsersPluginTests(unittest.TestCase):

    def setUp(self):
        setUpPasswordManagers()
        self.site = FakeSite()
        self.site['users'] = grok.Container()
        return

    def get_logger(self):
        logger = logging.getLogger('waeup.test')
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.addHandler(handler)
        return logger, stream

    def test_ifaces(self):
        # make sure we implement the promised interfaces
        plugin = UsersPlugin()
        verifyClass(IKofaPluggable, UsersPlugin)
        verifyObject(IKofaPluggable, plugin)
        return

    def test_update(self):
        # make sure user accounts are updated properly.
        plugin = UsersPlugin()
        logger, stream = self.get_logger()
        plugin.update(self.site, 'app', logger)
        stream.seek(0)
        self.assertEqual(stream.read(), '')
        self.site['users']['bob'] = FakeUserAccount()
        logger, stream = self.get_logger()
        plugin.update(self.site, 'app', logger)
        stream.seek(0)
        log_content = stream.read()
        self.assertTrue(hasattr(self.site['users']['bob'], 'description'))
        self.assertTrue(hasattr(self.site['users']['bob'], 'failed_logins'))
        self.assertTrue(
            isinstance(self.site['users']['bob'].failed_logins,
                       FailedLoginInfo))
        self.assertTrue('attribute description added' in log_content)
        self.assertTrue('attribute failed_logins added' in log_content)
        return
