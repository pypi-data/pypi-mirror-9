// -*- coding: utf-8 -*-
// :Progetto:  SoL --
// :Creato:    lun 29 apr 2013 08:21:57 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare SoL*/

Ext.define('SoL.view.Tourney', {
    requires: [
        'SoL.view.Boards',
        'SoL.view.Competitors',
        'SoL.view.Matches',
        'SoL.view.Ranking'
    ],

    statics: {
        configurators: function() {
            return [SoL.view.Boards.getConfig,
                    SoL.view.Competitors.getConfig,
                    SoL.view.Matches.getConfig,
                    SoL.view.Ranking.getConfig];
        }
    }
});
