# -*- coding: utf-8 -*-
# :Progetto:  SoL -- Rewritten tests for https://github.com/sublee/glicko2
# :Creato:    sab 07 dic 2013 14:35:47 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

import unittest
from sol.models.glicko2 import Glicko2, Rating, WIN, LOSS


class TestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.addTypeEqualityFunc(Rating, 'assertRatingEqual')

    def assertRatingEqual(self, rate1, rate2, msg=None):
        self.assertIsInstance(rate1, Rating, 'First argument is not a Rating')
        self.assertIsInstance(rate2, Rating, 'Second argument is not a Rating')

        self.assertAlmostEqual(rate1.mu, rate2.mu, delta=10**-3)
        self.assertAlmostEqual(rate1.phi, rate2.phi, delta=10**-3)
        self.assertAlmostEqual(rate1.sigma, rate2.sigma, delta=10**-5)


class TestGlicko2(TestCase):
    def test_glickman(self):
        env = Glicko2(tau=0.5)
        r1 = env.create_rating(1500, 200, 0.06)
        r2 = env.create_rating(1400, 30)
        r3 = env.create_rating(1550, 100)
        r4 = env.create_rating(1700, 300)
        rated = env.rate(r1, [(WIN, r2), (LOSS, r3), (LOSS, r4)])
        expected = env.create_rating(1464.051, 151.515, 0.05999)
        self.assertEqual(rated, expected)
