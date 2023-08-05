// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Players window
// :Creato:    ven 17 ott 2008 23:39:25 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare ngettext*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/
/*jsl:declare FileReader*/

Ext.define('SoL.module.Players.Actions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action',
        'Ext.form.field.File',
        'Ext.form.field.VTypes',
        'MP.form.Panel',
        'MP.window.Notification',
        'SoL.window.Help'
    ],

    statics: {
        EDIT_PLAYER_ACTION: 'edit_player',
        SHOW_DUPLICATED_ACTION: 'show_duplicates',
        SHOW_DISTRIBUTION_ACTION: 'show_distribution'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.editPlayerAction = me.addAction(new Ext.Action({
            itemId: ids.EDIT_PLAYER_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected player.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditPlayerWindow(record);
            }
        }));

        me.showDuplicatedPlayersAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_DUPLICATED_ACTION,
            text: _('Duplicates'),
            tooltip: _('Show possibly duplicated players that should be merged together.'),
            iconCls: 'dup-users-icon',
            needsCleanStore: true,
            handler: function() {
                var store = me.component.store;
                var win = me.component.up();

                if(this.dups) {
                    store.proxy.url = me.component.dataURL;
                    store.load();
                    this.setText(_('Duplicates'));
                    this.dups = false;
                    win.setTitle(_('Players'));
                } else {
                    var filterbar = me.component.findPlugin('filterbar');
                    if(filterbar) {
                        filterbar.clearFilters();
                    }
                    store.proxy.url = me.component.dataURL + '?dups=1';
                    store.load();
                    this.setText(_('Show all'));
                    this.dups = true;
                    win.setTitle(_('Possibly duplicated players'));
                }
            }
        }));

        me.showTourneysAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_TOURNEYS_ACTION,
            text: _('Tourneys'),
            tooltip: _('Show tourneys played by the selected player.'),
            iconCls: 'show-tourneys-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idplayer = record.get('idplayer');
                var player = SoL.module.Players.full_name(record);
                var module = me.module.app.getModule('tourneys-win');
                module.createOrShowWindow('players', idplayer, player);
            }
        }));

        me.showDistributionAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_DISTRIBUTION_ACTION,
            text: _('Distribution'),
            tooltip: _('Show players distribution around the globe.'),
            iconCls: 'players-distribution-icon',
            handler: function() {
                var desktop = me.module.app.getDesktop();
                var url = '/svg/playersdist?' + Ext.Object.toQueryString({
                    width: Math.floor(desktop.getWidth() * 0.8),
                    height: Math.floor(desktop.getHeight() * 0.8)
                });

                window.open(url, "_blank");
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ',
                 me.editPlayerAction,
                 me.showTourneysAction,
                 me.showDuplicatedPlayersAction,
                 me.showDistributionAction);

        me.component.on({
            itemdblclick: function() {
                if(!me.editPlayerAction.isDisabled())
                    me.editPlayerAction.execute();
            }
        });
        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditPlayerWindow(record);
            }
        });
    },

    shouldDisableAction: function(act) {
        var me = this;
        var disable = me.component.shouldDisableAction(act);
        var statics = me.statics();
        var currentuser = me.module.app.user;

        if(!disable && !currentuser.is_admin) {
            if(act.itemId == statics.EDIT_PLAYER_ACTION) {
                var record = me.component.getSelectionModel().getSelection()[0];

                if(record.get('idowner') != currentuser.user_id)
                    disable = true;
            }
        }

        return disable;
    },

    readImageAsDataURL: function(event, elt, form) {
        var file = elt.files[0];

        if(file.type.split('/')[0] == 'image') {
            var reader = new FileReader();

            form._portrait = file.name;

            reader.onload = function(e) {
                var img = e.target.result;
                if(img.length > 256000) {
                    Ext.MessageBox.alert(_('Error'),
                                         _('Image too big, max 256k allowed'));
                    form._portrait = null;
                } else {
                    form.down('image').setSrc(img);
                }
            };

            reader.onerror = function() {
                Ext.MessageBox.alert(_('Error'),
                                     _('Sorry, could not read image file')
                                     + ': ' + reader.error);
                form._portrait = null;
            };

            reader.readAsDataURL(file);
        } else {
            Ext.MessageBox.alert(_('Error'),
                                 _('Only image files allowed'));
        }
    },

    deleteImage: function(form) {
        form._portrait = '';
        form.down('image').setSrc('');
    },

    showEditPlayerWindow: function(record) {
        var me = this;
        var desktop = me.module.app.getDesktop();
        var win = desktop.getWindow('edit-player-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata;
        var size = desktop.getReasonableWindowSize(1000, 480);
        var editors = metadata.editors({
            '*': {
                editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%')
            },
            nationality: { editor: { xtype: 'flagscombo' } },
            Language: { editor: { queryMode: 'local' } }
        });
        var form = Ext.create('MP.form.Panel', {
            autoScroll: true,
            fieldDefaults: {
                labelWidth: 100,
                margin: '15 10 0 10'
            },
            items: [{
                xtype: 'container',
                layout: 'hbox',
                items: [{
                    xtype: 'container',
                    layout: 'anchor',
                    minHeight: 245,
                    flex: 1,
                    items: [
                        editors.firstname,
                        editors.lastname,
                        editors.nickname,
                        editors.password,
                        editors.sex,
                        editors.birthdate,
                        editors.email
                    ]
                }, {
                    xtype: 'container',
                    layout: 'anchor',
                    minHeight: 245,
                    flex: 1,
                    items: [
                        editors.phone,
                        editors.Language,
                        editors.nationality,
                        editors.citizenship,
                        editors.Club,
                        editors.Federation,
                        editors.Owner
                    ]
                }, {
                    xtype: 'container',
                    style: 'text-align: center;',
                    minHeight: 245,
                    width: 170,
                    items: [{
                        xtype: 'image',
                        margin: '50 10 0 10',
                        border: 1,
                        style: {
                            maxWidth: '150px',
                            maxHeight: '150px',
                            borderColor: 'lightgray',
                            borderStyle: 'solid'
                        }
                    }, {
                        xtype: 'filefield',
                        name: 'emblem',
                        fieldLabel: '',
                        labelWidth: 0,
                        buttonOnly: true,
                        buttonText: _('Change portrait…'),
                        style: 'text-align: center;',
                        listeners: {
                            afterrender: function(fld) {
                                var el = fld.fileInputEl.dom;
                                el.setAttribute('accept', 'image/*');
                            },
                            el: {
                                change: {
                                    fn: function(event, elt) {
                                        if(elt.files.length)
                                            me.readImageAsDataURL(event, elt, form);
                                    }
                                }
                            }
                        }
                    }, {
                        xtype: 'button',
                        text: _('Delete portrait'),
                        handler: function() {
                            me.deleteImage(form);
                        }
                    }]
                }]
            }],
            buttons: [{
                text: _('Cancel'),
                handler: function() {
                    if(record.phantom) {
                        record.store.deleteRecord(record);
                    }
                    win.close();
                }
            }, {
                text: _('Confirm'),
                formBind: true,
                handler: function() {
                    if(form.isValid()) {
                        form.updateRecord(record);
                        if(form._portrait !== undefined) {
                            record.set('portrait', form._portrait);
                            // Force the field as modified: the image name may be the same, but
                            // its content may be different. The backend needs the file name
                            // for logging purposes.
                            record.modified['portrait'] = '';
                            record.set('image', form.down('image').src);
                        }
                        win.close();
                        Ext.create("MP.window.Notification", {
                            position: 't',
                            width: 260,
                            title: _('Changes have been applied…'),
                            html: _('Your changes have been applied <strong>locally</strong>.<br/><br/>To make them permanent you must click on the <blink>Save</blink> button.'),
                            iconCls: 'info-icon'
                        }).show();
                    }
                }
            }]
        });

        win = desktop.createWindow({
            id: 'edit-player-win',
            title: _('Edit player'),
            iconCls: me.module.iconCls,
            width: size.width,
            height: size.height,
            modal: true,
            items: form,
            closable: false,
            minimizable: false,
            maximizable: false,
            resizable: false,
            tools: [{
                type: 'help',
                tooltip: _('Show user manual section.'),
                callback: function() {
                    var whsize = desktop.getReasonableWindowSize(800, 640);
                    var wh = Ext.create('SoL.window.Help', {
                        width: whsize.width,
                        height: whsize.height,
                        // TRANSLATORS: this is the URL of the manual
                        // page explaining championship insert/edit
                        help_url: _('/static/manual/en/players.html#insert-and-edit'),
                        title: _('Help on player insert/edit')
                    });
                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        if(!Ext.isEmpty(record.get('portrait')) || !Ext.isEmpty(record.get('image'))) {
            var portrait = form.down('image');
            if(!Ext.isEmpty(record.get('image'))) {
                portrait.setSrc(record.get('image'));
            } else {
                portrait.setSrc('/lit/portrait/' + record.get('portrait'));
            }
        }

        win.show();
    }
});

Ext.define('SoL.module.Players', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'Ext.grid.plugin.DragDrop',
        'SoL.form.field.FlagsCombo',
        'SoL.module.Players.Actions',
        'SoL.module.Players.MergePlugin',
        'SoL.window.Help'
    ],

    statics: {
        full_name: function(player, html) {
            var lastname = player.get('lastname');
            var firstname = player.get('firstname');
            var nickname = player.get('nickname');
            var format = function(fmt, data) {
                return fmt.replace(/\{(\w+)\}/g, function(m, i) {
                    return data[i];
                });
            };

            if(nickname !== '') {
                var nnlower = nickname.toLowerCase();
                var fnlower = firstname.toLowerCase();
                var lnlower = lastname.toLowerCase();
                if(nnlower != fnlower && nnlower != lnlower) {
                    nickname = format('“{nickname}”', {
                        nickname: nickname
                    });
                } else {
                    nickname = '';
                }
            } else {
                nickname = '';
            }

            if(html !== false) {
                if(nickname !== '') {
                    return format(
                        _('<b>{lastname}</b> {firstname} {nickname}'), {
                            lastname: lastname,
                            firstname: firstname,
                            nickname: nickname
                        });
                } else {
                    return format(_('<b>{lastname}</b> {firstname}'), {
                        lastname: lastname,
                        firstname: firstname
                    });
                }
            } else {
                if(nickname !== '') {
                    return format(_('{lastname} {firstname} {nickname}'), {
                        lastname: lastname,
                        firstname: firstname,
                        nickname: nickname
                    });
                } else {
                    return format(_('{lastname} {firstname}'), {
                        lastname: lastname,
                        firstname: firstname
                    });
                }
            }
        }
    },

    id: 'players-win',
    iconCls: 'players-icon',
    launcherText: function() {
        return _('Players');
    },
    launcherTooltip: function() {
        return _('<b>Players</b><br />Basic players management.');
    },

    config: {
        xtype: 'editable-grid',
        pageSize: 23,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/players',
        saveChangesURL: '/bio/saveChanges',
        sorters: ['lastname', 'firstname'],
        stripeRows: true,
        selType: 'checkboxmodel',
        viewConfig: {
            plugins: {
                ptype: 'mergeplayers'
            }
        }
    },

    getConfig: function(callback) {
        var me = this;
        var cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    Owner: { filter: false },
                    nationality: {
                        renderer: SoL.form.field.FlagsCombo.renderer,
                        filter: { type: 'combo', xtype: 'flagscombo', noOperatorPlugin: true,
                                  editable: true },
                        editor: { xtype: 'flagscombo' }
                    }
                };
                var fields = metadata.fields(overrides);

                fields.push({
                    name: 'image',
                    type: 'string',
                    sendBackToServer: true
                });

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: fields,
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('SoL.module.Players.Actions', {
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

    createOrShowWindow: function(filter_ids, buttons, idclub, club, isfederation) {
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
                var size = desktop.getReasonableWindowSize(690, 640, "SE");
                var filteredOn;

                config = Ext.apply({
                    selModel: {
                        listeners: {
                            selectionchange: function(model, records) {
                                var num = records.length;
                                var seltext = '';

                                if(num>0) {
                                    seltext = ' (' + Ext.String.format(ngettext(
                                        // TRANSLATORS: this is used on the Players window,
                                        // when there is a selection of one or more players.
                                        '{0} selected', '{0} selected', num
                                    ), num) + ')';
                                }
                                win.setTitle(me.getLauncherText() + filteredOn + seltext);
                            }
                        }
                    }
                }, config);

                if(filter_ids && filter_ids.length>0) {
                    config.stickyFilters = [{
                        id: 'ids',
                        property: "idplayer",
                        value: filter_ids.join(','),
                        operator: '<>'
                    }];
                }

                if(buttons) {
                    if(buttons.isPlugin) {
                        config.plugins = [buttons].concat(config.plugins);
                    } else {
                        config.buttons = buttons;
                    }
                }

                if(club) {
                    if(isfederation) {
                        filteredOn = ' (' + Ext.String.format(
                            // TRANSLATORS: this is the explanation on the players
                            // window title when the filter is a federation
                            _('associated with {0}'), club) + ')';
                        Ext.apply(config, {
                            newRecordData: {
                                idfederation: idclub,
                                Federation: club
                            },
                            stickyFilters: [{
                                property: 'idfederation',
                                value: idclub
                            }]
                        });
                    } else {
                        filteredOn = ' (' + Ext.String.format(
                            // TRANSLATORS: this is the explanation on the players
                            // window title when the filter is a club
                            _('members of {0}'), club) + ')';
                        Ext.apply(config, {
                            newRecordData: {
                                idclub: idclub,
                                Club: club
                            },
                            stickyFilters: [{
                                property: 'idclub',
                                value: idclub
                            }]
                        });
                    }
                } else {
                    filteredOn = '';
                }

                win = desktop.createWindow({
                    id: me.id,
                    title: (me.windowTitle || me.getLauncherText()) + filteredOn,
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
                                help_url: _('/static/manual/en/players.html'),
                                title: _('Help on players management')
                            });
                            wh.show();
                        }
                    }]
                });

                var grid = win.child('editable-grid');

                // Fetch the first page of records, and when done show
                // the window
                grid.store.load({
                    params: {start: 0, limit: me.pageSize},
                    callback: function() {
                        win.on({show: done, single: true});
                        win.show();
                    }
                });

                var da = grid.findActionById('delete');
                da.shouldBeDisabled = me.shouldDisableDeleteAction.bind(grid);
            }
        );
    },

    shouldDisableDeleteAction: function() {
        var grid = this;
        var sm = grid.getSelectionModel();
        var currentuser = grid.up().up().app.user;

        if(sm.getCount() > 0) {
            var selrecs = sm.getSelection();
            var disable = false;

            for(var i=selrecs.length-1; i>=0; i--) {
                var record = selrecs[i];

                if(!currentuser.is_admin && currentuser.user_id != record.get('idowner')) {
                    disable = true;
                    break;
                }
            }
            return disable;
        } else {
            return true;
        }
    }
});

Ext.define('SoL.module.Players.MergePlugin', {
    extend: 'Ext.grid.plugin.DragDrop',
    alias: 'plugin.mergeplayers',

    uses: [
        'Ext.view.DragZone',
        'SoL.module.Players.MergeTarget'
    ],

    ddGroup: 'player',

    onViewRender : function(view) {
        var me = this,
            scrollEl;

        if (me.enableDrag) {
            if (me.containerScroll) {
                scrollEl = view.getEl();
            }

            me.dragZone = new Ext.view.DragZone({
                view: view,
                ddGroup: me.dragGroup || me.ddGroup,
                containerScroll: me.containerScroll,
                scrollEl: scrollEl,
                getDragText: function() {
                    var count = this.dragData.records.length;
                    var msg = ngettext('{0} player', '{0} players', count);
                    return Ext.String.format(msg, count);
                }
            });
        }

        if (me.enableDrop) {
            me.dropZone = new SoL.module.Players.MergeTarget({
                view: view,
                ddGroup: me.dropGroup || me.ddGroup
            });
        }
    }

});

Ext.define('SoL.module.Players.MergeTarget', {
    extend: 'Ext.dd.DropTarget',
    uses: ['MP.window.Notification'],

    constructor: function(config) {
        var me = this;

        Ext.apply(me, config);

        me.callParent([me.view.el]);
    },

    _allowDrop: function(source, e, data) {
        //jsl:unused source
        var me = this;

        if(!e.hasModifier() || data.records.length===0) {
            return false;
        }

        var node = e.getTarget(me.view.getItemSelector());
        if(!node) {
            return false;
        }

        var app = me.view.up().up().up().app;
        var currentuser = app.user;
        if(!currentuser.is_admin) {
            for(var i=data.records.length-1; i>=0; i--) {
                if(currentuser.user_id != data.records[i].get('idowner')) {
                    return false;
                }
            }
        }

        var trec = me.view.getRecord(node);
        var tid = trec.get('idplayer');
        var sids = [];
        Ext.each(data.records, function(r) {
            sids.push(r.get('idplayer'));
        });
        if(sids.indexOf(tid) >= 0) {
            return false;
        }
        return [trec, data.records];
    },

    notifyDrop: function(source, e, data) {
        var me = this;

        var r = me._allowDrop(source, e, data);
        if(r===false) {
            return false;
        }
        var tdesc = SoL.module.Players.full_name(r[0]);
        var tid = r[0].get('idplayer');
        var sdescs = [];
        var sids = [];
        Ext.each(data.records, function(p) {
            sdescs.push(SoL.module.Players.full_name(p));
            sids.push(p.get('idplayer'));
        });

        var howmany = sids.length;
        Ext.MessageBox.confirm(
            _('Confirm players merge'),
            Ext.String.format(ngettext(
                'Player {0} will be replaced by {1} everywhere, if possible. Do you confirm?',
                'Players {0} will be replaced by {1} everywhere, if possible. Do you confirm?',
                howmany), Ext.toSentence(sdescs, _('and')), tdesc),
            function(response) {
                if('yes' == response) {
                    Ext.create("MP.window.Notification", {
                        position: 'br',
                        html: _('Merging selected players…'),
                        title: _('Please wait'),
                        iconCls: 'waiting-icon'
                    }).show();

                    Ext.Ajax.request({
                        url: '/bio/mergePlayers',
                        params: { tid: tid, sids: sids },
                        method: 'POST',
                        success: function (result) {
                            var res = Ext.decode(result.responseText);
                            var success, msg;
                            if(res) {
                                success = res.success;
                                msg = res.message;
                            } else {
                                success = false;
                                msg = _('Cannot decode JSON object');
                            }
                            if(success) {
                                Ext.create("MP.window.Notification", {
                                    position: 'br',
                                    iconCls: 'done-icon',
                                    title: _('Done'),
                                    html: msg
                                }).show();
                                me.view.store.reload();
                            } else {
                                Ext.create("MP.window.Notification", {
                                    position: 'br',
                                    iconCls: 'alert-icon',
                                    title: _('Error'),
                                    html: msg
                                }).show();
                            }
                        },
                        failure: function(result) {
                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                iconCls: 'alert-icon',
                                title: _('Error'),
                                html: result.statusText
                            }).show();
                        }
                    });
                }
            }
        );

        return true;
    },

    notifyOver: function(source, e, data) {
        return this._allowDrop(source, e, data)===false
            ? this.dropNotAllowed
            : this.dropAllowed;
    }
});


Ext.define('SoL.module.MyPlayers', {
    extend: 'SoL.module.Players',

    id: 'my-players-win',
    iconCls: 'players-icon',
    launcherText: null, // don't show an entry in the start menu

    init: function() {
        var me = this;
        var user = me.app.user;
        if(!me.config.orig_dataURL) me.config.orig_dataURL = me.config.dataURL;
        me.config.dataURL = Ext.String.urlAppend(me.config.orig_dataURL,
                                                 'filter_idowner=' + (user.is_admin
                                                                      ? 'NULL'
                                                                      : user.user_id));
        me.windowTitle = Ext.String.format(_('Players managed by {0}'), user.fullname);
        me.callParent();
    }
});


var phoneNumberRE = /^\+?([0-9]+ ?[0-9]+)*$/;
Ext.apply(Ext.form.field.VTypes, {
    phone: function(val, field) {
        return phoneNumberRE.test(val);
    },
    phoneText: _('This field should be a telephone number in the format "+39 123 456 7890"'),
    phoneMask: /[+\d ]/
});
