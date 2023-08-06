// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Ranking panel of the tourney management
// :Creato:    gio 20 nov 2008 18:24:44 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/

Ext.define('SoL.view.Ranking.Actions', {
    extend: 'MP.action.Plugin',
    uses: ['Ext.Action'],

    statics: {
        BY_NATIONALITY_ACTION: 'by_nationality',
        PRINT_RANKING_ACTION: 'print_ranking',
        PRINT_NATIONAL_RANKING_ACTION: 'print_national_ranking',
        PRINT_FINAL_BADGES_ACTION: 'print_final_badges',
        PRINT_FINAL_CARDS_ACTION: 'print_final_cards',
        PRIZE_GIVING_ACTION: 'prize_giving'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();
        var tourney = me.module.tourney;
        var tprized = tourney.prized;

        me.callParent();

        me.byNationalityAction = me.addAction(new Ext.Action({
            itemId: ids.BY_NATIONALITY_ACTION,
            text: _('By nationality'),
            tooltip: _("Toggle between normal ranking and grouped by competitor's nationality."),
            iconCls: 'toggle-by-nation-icon',
            handler: function() {
                me.component.toggleView(me.byNationalityAction);
            }
        }));

        me.printRankingAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_RANKING_ACTION,
            text: _('Ranking'),
            tooltip: _('Print current ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var turn = me.component.store.proxy.extraParams.turn;
                var url = '/pdf/ranking/' + tourney.idtourney;
                if(turn) url += '?turn=' + turn;
                window.location.assign(url);
            }
        }));

        me.printNationalRankingAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_NATIONAL_RANKING_ACTION,
            text: _('National ranking'),
            tooltip: _('Print current national ranking.'),
            iconCls: 'print-icon',
            handler: function() {
                var turn = me.component.store.proxy.extraParams.turn;
                var url = '/pdf/nationalranking/' + tourney.idtourney;
                if(turn) url += '?turn=' + turn;
                window.location.assign(url);
            }
        }));

        me.printFinalBadgesAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_FINAL_BADGES_ACTION,
            text: _('Badges'),
            tooltip: _('Print final badges with ranking and matches.'),
            iconCls: 'print-icon',
            hidden: !tprized,
            handler: function() {
                var url = '/pdf/badges/' + tourney.idtourney;
                window.location.assign(url);
            }
        }));

        me.printFinalCardsAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_FINAL_CARDS_ACTION,
            text: _('Finals'),
            tooltip: _('Print 1st/2nd and 3rd/4th place finals scorecards.'),
            iconCls: 'print-icon',
            hidden: !tprized && tourney.finals === null,
            handler: function() {
                var url = '/pdf/scorecards/' + tourney.idtourney;
                window.location.assign(url);
            }
        }));

        me.prizegivingAction = this.addAction(new Ext.Action({
            itemId: ids.PRIZE_GIVING_ACTION,
            text: tprized ? _('Reset prizes') : _('Assign prizes'),
            hidden: tourney.readOnly,
            tooltip: tprized
                ? _('Reset assigned final prizes.')
                : _('Assign final prizes.'),
            iconCls: 'prize-giving-icon',
            handler: function() {
                Ext.Ajax.request({
                    url: tprized
                        ? '/tourney/resetPrizes'
                        : '/tourney/assignPrizes',
                    params: { idtourney: tourney.idtourney },
                    success: function (r) {
                        var res = Ext.decode(r.responseText);

                        if(!res) {
                            Ext.MessageBox.alert(
                                _("Comunication error"),
                                _('Cannot decode JSON object'));
                        } else {
                            if(res.success) {
                                tourney.currentturn = res.currentturn;
                                tourney.rankedturn = res.rankedturn;
                                tourney.prized = tprized = res.prized;

                                me.component.store.reload();

                                if(tprized) {
                                    me.component.setWidth(500);
                                    me.prizegivingAction.setText(_('Reset prizes'));
                                    me.prizegivingAction.callEach(
                                        'setTooltip',
                                        [_('Reset assigned final prizes.')]);
                                } else {
                                    me.component.setWidth(me.component.initialConfig.width);
                                    me.prizegivingAction.setText(_('Assign prizes'));
                                    me.prizegivingAction.callEach(
                                        'setTooltip',
                                        [_('Assign final prizes.')]);
                                }
                            } else {
                                Ext.MessageBox.alert(_('Error'), res.message);
                            }
                        }
                    }
                });
        }}));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(0,
                 //me.byNationalityAction,
                 me.printFinalCardsAction,
                 me.printFinalBadgesAction,
                 me.printRankingAction,
                 me.printNationalRankingAction
                );

        if(!me.module.tourney.finals)
            me.component.addDocked({
                xtype: 'toolbar',
                dock: 'bottom',
                items: ['->', me.prizegivingAction]
            });
    }
});

Ext.define('SoL.view.Ranking', {
    extend: 'MP.grid.Panel',
    uses: ['SoL.view.Matches'],

    // requires: [
    //     'Ext.grid.feature.GroupingSummary'
    // ],

    alias: 'widget.ranking-grid',

    clicksToEdit: 1,

    statics: {
        getConfig: function(callback, errorcb, config) {
            //jsl:unused errorcb
            var me = this;
            var ordinal = SoL.view.Matches.ordinal;
            var cfg = config.Ranking = {
                dataURL: '/tourney/ranking',
                /*
                features: [{
                    ftype: 'groupingsummary',
                    id: 'bynationgrouping',
                    disabled: true,
                    hideGroupedHeader: true,
                    enableGroupingMenu: false,
                    showSummaryRow: true,
                    groupHeaderTpl: [
                        "{[SoL.form.field.FlagsCombo.renderer(values.name)]}"
                    ]
                }],
                remoteGroup: false,
                groupers: 'player1Nationality',
                */
                header: true,
                layout: 'fit',
                noAddAndDelete: true,
                noBottomToolbar: true,
                noFilterbar: true,
                pageSize: 999,
                plugins: [
                    Ext.create('SoL.view.Ranking.Actions', {
                        module: me
                    })
                ],
                remoteSort: false,
                saveChangesURL: '/bio/saveChanges',
                title: (config.tourney.rankedturn === 0
                        ? _('Ranking')
                        : (config.tourney.prized
                           ? _('Final ranking')
                           : Ext.String.format(
                               _('Ranking after {0} round'),
                               ordinal(config.tourney.rankedturn)))),
                xtype: 'ranking-grid'
            };

            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    // description: { summaryType: 'count',
                    //                summaryRenderer: function(value) {
                    //                    return Ext.String.format(
                    //                        ngettext('Totals for {0} competitor',
                    //                                 'Totals for {0} competitors',
                    //                                 value), value);
                    //                }
                    //              },
                    prize: { hidden: !config.tourney.prized,
                             //summaryType: 'sum',
                             editor: { hideTrigger: true }
                           } //,
                    //points: { summaryType: 'sum' },
                    //bucholz: { summaryType: 'sum' },
                    //netscore: { summaryType: 'sum' }
                };

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: metadata.fields(overrides),
                    columns: metadata.columns(overrides),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot
                });
                callback(cfg);
            });
        }
    },

    initEvents: function() {
        var me = this;
        var module = me.module;
        var tourney = module.tourney;
        var ordinal = SoL.view.Matches.ordinal;
        var normal_sorters = [
            { property: 'prize', direction: 'DESC' },
            { property: 'points', direction: 'DESC' },
            { property: 'bucholz', direction: 'DESC' },
            { property: 'netscore', direction: 'DESC' },
            { property: 'totscore', direction: 'DESC' },
            { property: 'rate', direction: 'DESC' },
            { property: 'description', direction: 'ASC' }
        ];
        var newturn_sorters = [
            { property: 'prize', direction: 'DESC' },
            { property: 'points', direction: 'DESC' },
            { property: 'bucholz', direction: 'DESC' },
            { property: 'rate', direction: 'DESC' },
            { property: 'netscore', direction: 'DESC' },
            { property: 'totscore', direction: 'DESC' },
            { property: 'description', direction: 'ASC' }
        ];

        me.callParent();

        me.on('itemdblclick', module.togglePlayerDetail, module);
        me.on('beforeedit', function() {
            return !tourney.readOnly && tourney.prized;
        });
        me.store.on('load', function(store) {
            var pcol = me.getColumnByName('prize');
            var turn = me.store.proxy.extraParams.turn;

            if(tourney.prized && !turn) {
                pcol.show();
            } else {
                pcol.hide();
            }

            if(turn) {
                if(turn <= tourney.delaytoppairing) {
                    // Reflect the actual ordering used to compute the next turn,
                    // see Tourney._makeNextTurn()
                    me.setTitle(Ext.String.format(_('Ranking used to compute {0} round'),
                                                  ordinal(turn+1)));
                    newturn_sorters = store.sort(newturn_sorters);
                } else {
                    me.setTitle(Ext.String.format(_('Ranking after {0} round'),
                                                  ordinal(turn)));
                    normal_sorters = store.sort(normal_sorters);
                }
            } else {
                me.setTitle((tourney.rankedturn === 0
                             ? _('Ranking')
                             : (tourney.prized
                                ? _('Final ranking')
                                : Ext.String.format(
                                    _('Ranking after {0} round'),
                                    ordinal(tourney.rankedturn)))));
                normal_sorters = store.sort(normal_sorters);
            }
        });

        Ext.tip.QuickTipManager.register({
            target: me.getView().getId(),
            text: _('Double click on a player to view his matches.'),
            width: 200,
            dismissDelay: 3000
        });
    },

    toggleView: function(action) {
        var me = this;
        var view = me.view;
        var feature = view.getFeature('bynationgrouping');

        if(feature.disabled) {
            feature.enable();
            action.setText(_('By nationality'));
        } else {
            feature.disable();
            action.setText(_('Normal'));
        }
    }
});
