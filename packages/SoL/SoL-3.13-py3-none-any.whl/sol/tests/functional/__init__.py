# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Functional tests
# :Creato:    lun 15 apr 2013 11:44:38 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from pyramid.paster import get_appsettings
from webtest import TestApp

from .. import TestCase


class FunctionalTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        from os.path import join
        from sol import main
        from tempfile import TemporaryDirectory

        super().setUpClass()

        cls._emblems_dir = TemporaryDirectory()
        with open(join(cls._emblems_dir.name, 'emblem.png'), 'w'):
            pass
        cls._portraits_dir = TemporaryDirectory()
        with open(join(cls._portraits_dir.name, 'portrait.png'), 'w'):
            pass
        settings = get_appsettings('../test.ini')
        settings['sol.emblems_dir'] = cls._emblems_dir.name
        settings['sol.portraits_dir'] = cls._portraits_dir.name
        cls.app = TestApp(main({}, **settings))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._emblems_dir.cleanup()
        cls._portraits_dir.cleanup()


class AuthenticatedTestCase(FunctionalTestCase):
    USERNAME = 'guest'
    PASSWORD = 'guest'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.app.post('/auth/login', {'username': cls.USERNAME,
                                     'password': cls.PASSWORD})
