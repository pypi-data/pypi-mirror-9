# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    sab 10 gen 2015 13:41:58 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from . import FunctionalTestCase


class TestStatics(FunctionalTestCase):

    def test_favicon(self):
        self.app.get('/favicon.ico')

    def test_robots(self):
        self.app.get('/robots.txt')
