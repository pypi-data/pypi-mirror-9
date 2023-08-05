// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Tourney competitors management
// :Creato:    gio 02 mag 2013 09:54:44 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare SoL*/

Ext.define('SoL.module.Competitors', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel',
        'SoL.window.Help'
    ],

    id: 'competitors-win',
    iconCls: 'edit-user-icon',
    // Don't show this module on the main menu
    launcherText: null,
    launcherTooltip: function() {
        return _("Tourney competitors management.");
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        dataURL: '/tourney/competitors',
        saveChangesURL: '/bio/saveChanges',
        noAddAndDelete: true,
        remoteSort: false,
        sorters: ['player1FullName'],
        stripeRows: true
    },

    getConfig: function(callback, errorcb, config) {
        //jsl:unused errorcb
        var me = this;
        var cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    retired: { hidden: true, readonly: true },
                    player1Nationality: {
                        renderer: SoL.form.field.FlagsCombo.renderer
                    },
                    player1FullName: { flex: 1 },
                    player2FullName: function() {
                        return { flex: 1, hidden: config.playersperteam < 2 };
                    },
                    player3FullName: function() {
                        return { flex: 1, hidden: config.playersperteam < 3 };
                    },
                    player4FullName: function() {
                        return { flex: 1, hidden: config.playersperteam < 4 };
                    },
                    '*': {
                        editor: function(finfo) {
                            var c = {};
                            if(finfo.name.substr(7) !== 'FullName')
                                c.readonly = true;
                            return c;
                        }
                    }
                };
                var columns = metadata.columns(overrides).filter(function(c) {
                    return c.dataIndex != 'player1Country';
                });

                Ext.apply(cfg, {
                    fields: metadata.fields(overrides),
                    columns: columns,
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot
                });
                callback(cfg);
                me.app.on('logout', function() { delete cfg.metadata; }, me, { single: true });
            });
        } else {
            callback(cfg);
        }
    },

    createOrShowWindow: function(idtourney, tourney, date, championship, playersperteam) {
        var me = this;
        var config = me.config;
        var desktop = me.app.getDesktop();
        var win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        me.configure(
            [me.getConfig],
            function(done) {
                var size = desktop.getReasonableWindowSize(650, 447, "NE");

                config = Ext.apply({
                    stickyFilters: [{
                        property: 'idtourney',
                        value: idtourney
                    }]
                }, config);

                win = desktop.createWindow({
                    id: me.id,
                    title: Ext.String.format(
                        // TRANSLATORS: {0} is the tourney description, {1} the
                        // championship description and {2} the date of the tourney
                        _('Competitors of tourney “{0}” ({1}), {2}'),
                        tourney, championship, MP.data.MetaData.renderDate(date)),
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
                                help_url: _('/static/manual/en/competitors.html'),
                                title: _('Help on competitors management')
                            });
                            wh.show();
                        }
                    }]
                });

                // Fetch the first page of records, and when done show
                // the window
                win.child('editable-grid').store.load({
                    params: {start: 0, limit: me.pageSize},
                    callback: function() {
                        win.on({show: done, single: true});
                        win.show();
                    }
                });
            }, { playersperteam: playersperteam });
    }
});
