// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Authentication form controller
// :Creato:    lun 15 apr 2013 11:33:59 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare SoL*/
/*jsl:declare _*/
/*jsl:declare window*/

Ext.define('SoL.desktop.App', {
    extend: 'MP.desktop.App',

    desktopConfig: {
        wallpaper: '/static/images/wallpapers/scr.png',
        wallpaperStyle: 'center'
    },

    getStartConfig: function () {
        var config = this.callParent();

        config.height = 165;
        return config;
    },

    getToolConfig: function() {
        var me = this;
        var config = me.callParent();
        var upload_module = me.getModule('upload-win');

        config.items.unshift({
            text: _('Scorecards'),
            tooltip: _('Print one sheet of blank scorecards.'),
            iconCls: 'print-icon',
            handler: function() {
                var url = '/pdf/scorecards/blank';
                window.location.assign(url);
            }
        }, '-', {
            text: _('Manual'),
            tooltip: _('Show user manual.'),
            iconCls: 'help-icon',
            handler: function() {
                // TRANSLATORS: this is the URL of the user manual
                window.open(_('/static/manual/en/index.html'), "_blank");
            }
        }, {
            text: _('Rules'),
            tooltip: _('Carrom playing rules.'),
            iconCls: 'info-icon',
            handler: function() {
                // TRANSLATORS: this is the URL of the carrom rules chapter in
                // the user manual
                window.open(_('/static/manual/en/rules.html'), "_blank");
            }
        }, '-');

        if(upload_module) {
            config.items.unshift({
                iconCls: upload_module.iconCls,
                text: _('Upload'),
                tooltip: upload_module.getLauncherTooltip(),
                handler: upload_module.createOrShowWindow,
                scope: upload_module
            });
        }

        return config;
    }
});


Ext.define('SoL.controller.Login', {
    extend: 'MP.controller.Login',

    applicationClass: 'SoL.desktop.App',

    _doCreateUserDesktop: function(user) {
        var me = this;
        var app = MP.controller.Login.prototype.createUserDesktop.call(me, user);

        app.on('ready', function() {
            Ext.Ajax.request({
                url: '/data/countries',
                success: function(response) {
                    var result = Ext.decode(response.responseText);
                    var root = result.root;
                    var c, cd = {};

                    for(var i=0, l=result.count; i<l; i++) {
                        c = root[i];
                        cd[c.code] = c.name;
                    }
                    SoL.form.field.FlagsCombo.countries = cd;
                }
            });
        });
    },

    createUserDesktop: function(user) {
        var me = this;
        var reload = user.reload_l10n;

        delete user.reload_l10n;

        // Maybe reload the l10n catalogs, to match logged user prefs

        if(reload) {
            Ext.Loader.loadScript({
                url: '/catalog',
                onLoad: function() {
                    Ext.Loader.loadScript({
                        url: '/extjs-l10n',
                        onLoad: function() {
                            me._doCreateUserDesktop(user);
                        }
                    });
                }
            });
        } else {
            me._doCreateUserDesktop(user);
        }
    }
});
