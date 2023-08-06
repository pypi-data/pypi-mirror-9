//-*- coding: utf-8 -*-
//:Progetto:  SoL -- Rated players window
//:Creato:    dom 15 dic 2013 18:08:06 CET
//:Autore:    Lele Gaifax <lele@metapensiero.it>
//:Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare SoL*/
/*jsl:declare _*/
/*jsl:declare window*/

Ext.define('SoL.module.RatedPlayers.Actions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action'
    ],

    statics: {
        SHOW_CHART_ACTION: 'show_chart',
        SHOW_RANKING_ACTION: 'show_ranking'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.showChartAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_CHART_ACTION,
            text: _('Chart'),
            tooltip: _('Show the rating chart of selected players.'),
            iconCls: 'rating-chart-icon',
            needsSelectedRow: true,
            disabled: true,
            handler: function() {
                var idrating = me.module.idrating;
                var sels = me.component.getSelectionModel().getSelection();
                var players = [];
                var desktop = me.module.app.getDesktop();

                for(var i=0, l=sels.length; i<l; i++) {
                    var id = sels[i].get('idplayer');
                    players.push(id);
                }

                var url = '/svg/ratingchart/' + idrating + '?' + Ext.Object.toQueryString({
                    idplayer: players,
                    width: Math.floor(desktop.getWidth() * 0.8),
                    height: Math.floor(desktop.getHeight() * 0.8)
                });

                window.open(url, "_blank");
            }
        }));

        me.showRankingAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_RANKING_ACTION,
            text: _('Print'),
            tooltip: _('Print this rating ranking.'),
            iconCls: 'print-championship-icon',
            handler: function() {
                var idrating = me.module.idrating;
                var url = '/pdf/ratingranking/' + idrating;
                window.open(url, "_blank");
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');
        tbar.add(2, ' ', me.showChartAction, me.showRankingAction);
    }
});

Ext.define('SoL.module.RatedPlayers', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.RatedPlayers.Actions',
        'SoL.window.Help'
    ],

    id: 'rated-players-win',
    iconCls: 'rated-players-icon',
    launcherText: null,
    launcherTooltip: function() {
        return _('Players rates.');
    },

    config: {
        xtype: 'basic-grid',
        pageSize: 14,
        readOnly: true,
        dataURL: '/data/ratedPlayers',
        sorters: [{ property: 'rate', direction: 'DESC' }],
        stripeRows: true,
        selType: 'checkboxmodel'
    },

    getConfig: function(callback) {
        var me = this;
        var cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    nationality: {
                        renderer: SoL.form.field.FlagsCombo.renderer
                    }
                };

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: metadata.fields(overrides),
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('SoL.module.RatedPlayers.Actions', {
                            module: me
                        })
                    ]
                });
                callback(cfg);
                me.app.on('logout', function() { delete cfg.metadata; }, me, { single: true });
            });
        } else {
            callback(cfg);
        }
    },

    createOrShowWindow: function(idrating, rating) {
        var me = this;
        var config = me.config;
        var desktop = me.app.getDesktop();
        var win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        me.idrating = idrating;

        me.configure(
            [me.getConfig],
            function(done) {
                var size = desktop.getReasonableWindowSize(690, 421, "SE");

                config = Ext.apply({
                    stickyFilters: [{
                        property: 'idrating',
                        value: idrating
                    }]
                }, config);

                win = desktop.createWindow({
                    id: me.id,
                    title: Ext.String.format(
                        // TRANSLATORS: {0} is the description of the rating
                        _('Players in rating “{0}”'), rating),
                    taskbuttonTooltip: me.getLauncherTooltip(),
                    iconCls: me.iconCls,
                    items: [config],
                    x: size.x,
                    y: size.y,
                    width: size.width,
                    height: size.height,
                    tools: [{
                        type: 'help',
                        tooltip: _('Show user manual section.'),
                        callback: function() {
                            var whsize = desktop.getReasonableWindowSize(800, 640);
                            var wh = Ext.create('SoL.window.Help', {
                                width: whsize.width,
                                height: whsize.height,
                                // TRANSLATORS: this is the URL of the manual
                                // page explaining players management
                                help_url: _('/static/manual/en/playersrates.html'),
                                title: _('Help on rated players window')
                            });
                            wh.show();
                        }
                    }]
                });

                // Fetch the first page of records, and when done show
                // the window
                win.child('basic-grid').store.load({
                    params: {start: 0, limit: me.pageSize},
                    callback: function() {
                        win.on({show: done, single: true});
                        win.show();
                    }
                });
            }
        );
    }
});
