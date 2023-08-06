# -*- coding: utf-8 -*-
# :Progetto:  SoL
# :Creato:    mar 18 nov 2008 14:08:52 CET
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#


class OperationAborted(RuntimeError):
    "Exception raised on operation errors."


class LoadError(OperationAborted):
    "Exception raised on load operations."


class TourneyAlreadyExistsError(LoadError):
    "Exception raised trying to load an already existing tourney."

    def __init__(self, message, tourney):
        super().__init__(message)
        self.tourney = tourney


class UnauthorizedOperation(OperationAborted):
    "Exception raised trying to modify a record not owned."
