// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Tourney management window
// :Creato:    gio 20 nov 2008 18:21:20 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare SoL*/

Ext.define('SoL.module.Tourney', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'Ext.layout.container.Border',
        'SoL.view.Tourney',
        'SoL.window.Help'
    ],

    id: 'tourney-win',
    iconCls: 'tourney-icon',
    launcherText: null,
    launcherTooltip: function() {
        return _('<b>Tourney</b><br />Tourney management.');
    },

    createOrShowWindow: function(tourney) {
        var me = this;
        var desktop = me.app.getDesktop();
        var win = desktop.getWindow(me.id);
        var winWidth = desktop.getWidth();
        var winHeight = desktop.getHeight() - desktop.taskbar.getHeight();
        var currentuser = me.app.user;
        var readonly = (!currentuser.is_admin &&
                        tourney.get('idowner') != currentuser.user_id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        // Keep a copy of the raw data
        me.tourney = tourney.getData();
        me.tourney.readOnly = readonly;

        me.configure(SoL.view.Tourney.configurators(), function(done, config) {
            var tfilter = {
                filter_idtourney: me.tourney.idtourney
            };

            Ext.apply(config.Boards, {
                collapsed: true,
                collapsible: true,
                module: me,
                region: 'south',
                split: true,
                extraParams: tfilter
            });
            config.Boards.items[0].store.proxy.extraParams = tfilter;

            Ext.apply(config.Competitors, {
                collapsed: me.tourney.currentturn > 0,
                collapsible: true,
                module: me,
                region: 'west',
                split: true,
                width: winWidth*0.3 < 281 ? winWidth*0.3 : 280
            });
            config.Competitors.items[0].store.proxy.extraParams = tfilter;

            Ext.apply(config.Matches, {
                border: false,
                module: me,
                region: 'center',
                extraParams: tfilter
            });

            Ext.apply(config.Ranking, {
                collapsed: !(me.tourney.prized || me.tourney.currentturn !== 0),
                collapsible: true,
                module: me,
                region: 'east',
                split: true,
                width: (winWidth*0.3 < 351 ? winWidth*0.3 : 350)
                    + (me.tourney.prized ? 150 : 0),
                extraParams: tfilter
            });

            win = desktop.createWindow({
                id: me.id,
                title: (me.tourney.Championship
                        + ': "'
                        + me.tourney.description
                        + '", ' +
                        MP.data.MetaData.renderDate(me.tourney.date)),
                taskbuttonTooltip: me.getLauncherTooltip(),
                iconCls: me.iconCls,
                width: winWidth,
                height: winHeight,
                layout: 'border',
                items: [
                    config.Boards,
                    config.Competitors,
                    config.Matches,
                    config.Ranking
                ],
                tools: [{
                    type: 'help',
                    tooltip: _('Show user manual section.'),
                    callback: function() {
                        var whsize = desktop.getReasonableWindowSize(800, 640);
                        var wh = Ext.create('SoL.window.Help', {
                            width: whsize.width,
                            height: whsize.height,
                            // TRANSLATORS: this is the URL of the manual
                            // page explaining tourney management
                            help_url: _('/static/manual/en/tourney.html'),
                            title: _('Help on tourney management')
                        });
                        wh.show();
                    }
                }]
            });

            var mgrid = me.matches_grid = win.query('editable-grid[dataURL=/tourney/matches]')[0];
            var rgrid = win.query('editable-grid[dataURL=/tourney/ranking]')[0];
            var cview = win.query('competitors-dataview')[0];

            rgrid.store.on('beforeload', function(store, operation) {
                // remove the sorters, we do local sort...
                // silly ExtJS 4.2.1!
                operation.sorters = undefined;
            });

            var updtitle = function(store) {
                var nrecs = store.data.length;
                var eastp = cview.ownerCt;
                eastp.setTitle(Ext.String.format(_('Competitors ({0})'),
                                                 nrecs));
            };
            cview.store.on('add', updtitle);
            cview.store.on('load', updtitle);
            cview.store.on('remove', updtitle);

            var ready = -3;
            var cb = function() {
                ready++;
                if(ready === 0) {
                    win.on('show', function() {
                        done();
                        rgrid.store.on('load', function() {
                            if(me.tourney.rankedturn > 0) {
                                cview.ownerCt.collapse();
                                rgrid.expand();
                            } else {
                                cview.ownerCt.expand();
                                rgrid.collapse();
                            }
                        });
                    }, me, {single: true});
                    win.show();
                }
            };

            mgrid.store.on({
                load: function(s, recs, opts) {
                    if(!mgrid.focusedCompetitor) {
                        var ordinalp = SoL.view.Matches.ordinalp;
                        if(Ext.isEmpty(recs)) {
                            mgrid.setTitle(Ext.String.format(_('Matches')));
                        } else if(recs[0].get('final')) {
                            mgrid.setTitle(Ext.String.format(_('Matches {0} final round'),
                                                             ordinalp(recs[0].get('turn'))));
                        } else {
                            mgrid.setTitle(Ext.String.format(_('Matches {0} round'),
                                                             ordinalp(recs[0].get('turn'))));
                        }
                    }
                }
            });


            cview.store.on('load', function(s, recs) {
                me.tourney.partecipants = recs.length;
                mgrid.updateActions();
            });

            cview.store.load({callback: cb});
            mgrid.store.load({callback: cb});
            rgrid.store.load({callback: cb});

            me.reloadRanking = function(turn) {
                var ep = rgrid.store.proxy.extraParams;
                if(turn && turn != me.tourney.rankedturn) {
                    ep['turn'] = turn < me.tourney.rankedturn ? turn : me.tourney.rankedturn;
                } else {
                    delete ep['turn'];
                }
                rgrid.store.reload();
            };

            me.reloadMatches = function() {
                mgrid.store.reload();
            };

            rgrid.store.on('load', function() {
                mgrid.updateActions();
            });

            me.togglePlayerDetail = function(grid, record) {
                //jsl:unused grid
                var idc = record.get('idcompetitor');
                var mstore = mgrid.store;

                if(!mgrid.focusedCompetitor || mgrid.focusedCompetitor != idc) {
                    mgrid.setTitle(Ext.String.format(
                        _('Matches played by {0}'), record.get('description')));
                    mstore.clearFilter(true);
                    if(!mgrid.focusedCompetitor) {
                        mgrid.child('toolbar[dock="left"]').hide();
                        mgrid.getColumnByName('turn').show();
                        mgrid.getColumnByName('board').hide();
                        mstore.load({
                            scope: mstore,
                            callback: function() {
                                this.filterBy(function(rec) {
                                    return rec.get('idcompetitor1') == idc
                                        || rec.get('idcompetitor2') == idc;
                                });
                            }
                        });
                    } else {
                        mstore.filterBy(function(rec) {
                            return rec.get('idcompetitor1') == idc
                                || rec.get('idcompetitor2') == idc;
                        });
                    }
                    mgrid.focusedCompetitor = idc;
                } else {
                    var turn = mgrid.filteredTurn || me.tourney.currentturn;

                    mgrid.child('toolbar[dock="left"]').show();
                    mgrid.getColumnByName('turn').hide();
                    mgrid.getColumnByName('board').show();
                    mstore.filter({
                        id: 'turn',
                        property: 'turn',
                        value: turn
                    });
                    mgrid.focusedCompetitor = null;
                }
            };

            if(!me.tourney.prized && !readonly) {
                var newturn = mgrid.findActionById('new_turn');
                var printbadges = cview.findActionById('print_badges');
                var printfbadges = rgrid.findActionById('print_final_badges');
                var printfcards = rgrid.findActionById('print_final_cards');
                var rsave = rgrid.findActionById('save');
                var rrestore = rgrid.findActionById('restore');

                cview.store.on('update', function(store, record, action) {
                    //jsl:unused store
                    //jsl:unused record
                    if(action=='commit' || action=='reject') {
                        newturn.setDisabled(false);
                    } else {
                        newturn.setDisabled(true);
                    }
                });
                cview.store.on('reject', function() {
                    newturn.setDisabled(false);
                });

                mgrid.store.on('update', function(store, record, action) {
                    //jsl:unused store
                    //jsl:unused record
                    if(action=='commit' || action=='reject') {
                        newturn.setDisabled(false);
                    } else {
                        newturn.setDisabled(true);
                    }
                });
                mgrid.store.on('reject', function() {
                    newturn.setDisabled(false);
                });

                rgrid.store.on('load', function() {
                    var prized = me.tourney.prized;
                    var finals = me.tourney.finals;
                    printbadges.setHidden(prized);
                    printfbadges.setHidden(!prized);
                    printfcards.setDisabled(!me.tourney.finalturns);
                    printfcards.setHidden(finals===0
                                          || (finals && prized)
                                          || (!finals && !prized));
                    rsave.setHidden(!prized);
                    rrestore.setHidden(!prized);
                });
            }
        }, { tourney: me.tourney });
    }
});
