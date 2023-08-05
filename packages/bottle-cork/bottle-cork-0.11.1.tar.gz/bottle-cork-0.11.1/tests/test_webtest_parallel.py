# Cork - Authentication module for the Bottle web framework
# Copyright (C) 2013 Federico Ceratto and others, see AUTHORS file.
# Released under LGPLv3+ license, see LICENSE.txt
#
# Functional test using Json backend
#
# Requires WebTest http://webtest.pythonpaste.org/
#
# Run as: nosetests functional_test.py
#

from nose import SkipTest
from time import time
from datetime import datetime
from webtest import TestApp
import glob
import json
import os
import shutil

import testutils
from cork import Cork

REDIR = 302

class Test(testutils.WebFunctional):
    def __init__(self):
        self._tmpdir = None
        self._tmproot = None
        self._app = None
        self._starting_dir = os.getcwd()

    def populate_conf_directory(self):
        """Populate a directory with valid configuration files, to be run just once
        The files are not modified by each test
        """
        self._tmpdir = os.path.join(self._tmproot, "cork_functional_test_source")

        # only do this once, as advertised
        if os.path.exists(self._tmpdir):
            return

        os.mkdir(self._tmpdir)
        os.mkdir(self._tmpdir + "/example_conf")

        cork = Cork(os.path.join(self._tmpdir, "example_conf"), initialize=True)

        cork._store.roles['admin'] = 100
        cork._store.roles['editor'] = 60
        cork._store.roles['user'] = 50
        cork._store.save_roles()

        tstamp = str(datetime.utcnow())
        username = password = 'admin'
        cork._store.users[username] = {
            'role': 'admin',
            'hash': cork._hash(username, password),
            'email_addr': username + '@localhost.local',
            'desc': username + ' test user',
            'creation_date': tstamp
        }
        username = password = ''
        cork._store.users[username] = {
            'role': 'user',
            'hash': cork._hash(username, password),
            'email_addr': username + '@localhost.local',
            'desc': username + ' test user',
            'creation_date': tstamp
        }
        cork._store.save_users()

    def remove_temp_dir(self):
        p = os.path.join(self._tmproot, 'cork_functional_test_wd')
        for f in glob.glob('%s*' % p):
            #shutil.rmtree(f)
            pass

    @classmethod
    def setUpClass(cls):
        print("Setup class")

    def setup(self):
        # create test dir and populate it using the example files

        # save the directory where the unit testing has been run
        if self._starting_dir is None:
            self._starting_dir = os.getcwd()

        # create json files to be used by Cork
        self._tmproot = testutils.pick_temp_directory()
        assert self._tmproot is not None

        # purge the temporary test directory
        self.remove_temp_dir()

        self.populate_temp_dir()
        self.create_app_instance()
        self._app.reset()
        print("Reset done")
        print("Setup completed")

    def populate_temp_dir(self):
        """populate the temporary test dir"""
        assert self._tmproot is not None
        assert self._tmpdir is None

        tstamp = str(time())[5:]
        self._tmpdir = os.path.join(self._tmproot, "cork_functional_test_wd_%s" % tstamp)

        try:
            os.mkdir(self._tmpdir)
        except OSError:
            # The directory is already there, purge it
            print("Deleting %s" % self._tmpdir)
            shutil.rmtree(self._tmpdir)
            os.mkdir(self._tmpdir)

            #p = os.path.join(self._tmproot, 'cork_functional_test_wd')
            #for f in glob.glob('%s*' % p):
            #    shutil.rmtree(f)

        # copy the needed files
        shutil.copytree(
            os.path.join(self._starting_dir, 'tests/example_conf'),
            os.path.join(self._tmpdir, 'example_conf')
        )
        shutil.copytree(
            os.path.join(self._starting_dir, 'tests/views'),
            os.path.join(self._tmpdir, 'views')
        )

        # change to the temporary test directory
        # cork relies on this being the current directory
        os.chdir(self._tmpdir)

        print("Test directory set up")

    def create_app_instance(self):
        """create TestApp instance"""
        assert self._app is None
        import simple_webapp
        self._bottle_app = simple_webapp.app
        self._app = TestApp(self._bottle_app)
        print("Test App created")

    def teardown(self):
        print("Doing teardown")
        try:
            self._app.post('/logout')
        except:
            pass

        # drop the cookie
        self._app.reset()
        assert 'beaker.session.id' not in self._app.cookies, "Unexpected cookie found"
        # drop the cookie
        self._app.reset()

        #assert self._app.get('/admin').status != '200 OK'
        os.chdir(self._starting_dir)
        #if self._tmproot is not None:
        #    testutils.purge_temp_directory(self._tmproot)

        self._app.app.options['timeout'] = self._default_timeout
        self._app = None
        self._tmproot = None
        self._tmpdir = None
        print("Teardown done")

    def setup(self):
        # create test dir and populate it using the example files

        # save the directory where the unit testing has been run
        if self._starting_dir is None:
            self._starting_dir = os.getcwd()

        # create json files to be used by Cork
        self._tmproot = testutils.pick_temp_directory()
        assert self._tmproot is not None

        # purge the temporary test directory
        self.remove_temp_dir()

        self.populate_temp_dir()
        self.create_app_instance()
        self._app.reset()
        print("Reset done")
        self._default_timeout = self._app.app.options['timeout']
        print("Setup completed")

    def assert_200(self, path, match):
        """Assert that a page returns 200"""
        p = self._app.get(path)
        assert p.status_int == 200, "Status: %d, Location: %s" % \
            (p.status_int, p.location)

        if match is not None:
            assert match in p.body, "'%s' not found in body: '%s'" % (match, p.body)

        return p

    def assert_redirect(self, page, redir_page, post=None):
        """Assert that a page redirects to another one"""

        # perform GET or POST
        if post is None:
            p = self._app.get(page, status=302)
        else:
            assert isinstance(post, dict)
            p = self._app.post(page, post, status=302)

        dest = p.location.split(':80/')[-1]
        dest = "/%s" % dest
        assert dest == redir_page, "%s redirects to %s instead of %s" % \
            (page, dest, redir_page)

        return p

    def login_as_admin(self):
        """perform log in"""
        assert self._app is not None
        assert 'beaker.session.id' not in self._app.cookies, "Unexpected cookie found"

        self.assert_200('/login', 'Please insert your credentials')
        assert 'beaker.session.id' not in self._app.cookies, "Unexpected cookie found"

        self.assert_redirect('/admin', '/sorry_page')

        self.assert_200('/user_is_anonymous', 'True')
        assert 'beaker.session.id' not in self._app.cookies, "Unexpected cookie found"

        post = {'username': 'admin', 'password': 'admin'}
        self.assert_redirect('/login', '/', post=post)
        assert 'beaker.session.id' in self._app.cookies, "Cookie not found"

        import bottle
        session = bottle.request.environ.get('beaker.session')
        print("Session from func. test", repr(session))

        self.assert_200('/login', 'Please insert your credentials')


        p = self._app.get('/admin')
        assert 'Welcome' in p.body, repr(p)

        p = self._app.get('/my_role', status=200)
        assert p.status == '200 OK'
        assert p.body == 'admin', "Sta"

        print("Login performed")

    def test_functional_expiration(self):
        self.login_as_admin()
        r = self._app.get('/admin')
        assert r.status == '200 OK', repr(r)
        # change the cookie expiration in order to expire it
        self._app.app.options['timeout'] = 0
        assert self._app.get('/admin').status_int == REDIR, "The cookie should have expired"



