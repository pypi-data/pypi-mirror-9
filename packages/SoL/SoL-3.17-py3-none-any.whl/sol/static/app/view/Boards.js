// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Boards panel of the tourney management
// :Creato:    gio 20 nov 2008 18:26:21 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare SoL*/

Ext.define('SoL.view.Boards.Actions', {
    extend: 'MP.action.SaveAndReset',
    uses: ['Ext.Action'],

    attachActions: function() {
        var me = this;

        me.callParent();

        var panel = me.component.up('panel');
        var tbar = panel.child('#ttoolbar');

        tbar.add(0, '->',
                 me.saveAction,
                 me.restoreAction);

        if(!panel.module.tourney.prized) {
            var store = me.component.store;

            store.on('update', function(s, r, action) {
                //jsl:unused s
                //jsl:unused r
                if(action=='edit') {
                    me.saveAction.setDisabled(false);
                    me.restoreAction.setDisabled(false);
                }
            });
            store.on('load', function() {
                me.saveAction.setDisabled(true);
                me.restoreAction.setDisabled(true);
            });
            store.on('reject', function() {
                me.saveAction.setDisabled(true);
                me.restoreAction.setDisabled(true);
            });
        }
    }
});


Ext.define('SoL.view.Boards', {
    extend: 'Ext.view.View',
    requires: [
        'SoL.view.Boards.Actions'
    ],

    alias: 'widget.boards-dataview',

    autoHeight: true,
    autoScroll: true,
    ddGroup: 'competitor',
    deferEmptyText: false,
    emptyText: _('Only first round pairings can be manually adjusted.'),
    itemSelector: 'div.board',
    singleSelect: true,

    tpl: [
        '<tpl for=".">',
        '<div class="board{dirtyCls}" id="match_{idcompetitor1}" mid="{idmatch}">',
        '<span class="board-number">', _('Board #{board}'), '</span>',
        '<span class="competitor" id="c_1_{idcompetitor1}">{competitor1FullName}</span>',
        '<span class="carrom-board"></span>',
        '<span class="competitor" id="c_2_{idcompetitor2}">{competitor2FullName}</span>',
        '</div>',
        '</tpl>',
        '<div class="x-clear"></div>'
    ],

    statics: {
        getConfig: function(callback, errorcb, config) {
            //jsl:unused errorcb
            var me = this;
            var dataURL = '/tourney/boards';
            var dataview = {
                saveChangesURL: '/bio/saveChanges',
                xtype: 'boards-dataview',
                id: 'boards-view',
                listeners: {
                    destroy: function(v) {
                        v.dragZone.destroy();
                    },

                    render: function(v) {
                        v.dragZone = new Ext.dd.DragZone(v.getEl(), {
                            ddGroup: 'competitor',

                            getDragData: function(e) {
                                var player = e.getTarget('span.competitor', 10, true);
                                if (player) {
                                    var container = player.parent();
                                    var idmatch = parseInt(container.dom.attributes.mid.nodeValue, 10);
                                    var match = v.store.getById(idmatch);
                                    var xy = player.getXY();
                                    var sourceEl = player.dom;
                                    var d = sourceEl.cloneNode(true);
                                    d.id = Ext.id();
                                    return {
                                        sourceEl: sourceEl,
                                        sourceMatch: match,
                                        repairXY: xy,
                                        ddel: d
                                    };
                                } else {
                                    return null;
                                }
                            },

                            getRepairXY: function() {
                                return this.dragData.repairXY;
                            }
                        });
                    }
                },
                plugins: [ Ext.create('SoL.view.Boards.Actions') ]
            };

            var cfg = config.Boards = {
                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'top',
                    itemId: 'ttoolbar',
                    enableOverflow: true
                }],
                hidden: config.tourney.readOnly || config.tourney.currentturn > 1,
                items: [ dataview ],
                layout: 'fit',
                title: _('First round pairings'),
                titleCollapse: false,
                floatable: false,
                xtype: 'panel'
            };

            MP.data.MetaData.fetch(dataURL, me, function(metadata) {
                var overrides = {};
                var model;

                model = Ext.define('MP.data.ImplicitModel-' + Ext.id(), {
                    extend: 'Ext.data.Model',
                    fields: metadata.fields(overrides),
                    idProperty: metadata.primary_key
                });

                dataview.store = Ext.create('MP.data.Store', {
                    model: model,
                    proxy: {
                        type: 'ajax',
                        url: dataURL,
                        reader: {
                            type: 'json',
                            idProperty: metadata.primary_key,
                            totalProperty: metadata.count_slot,
                            successProperty: metadata.success_slot,
                            root: metadata.root_slot
                        }
                    },
                    autoDestroy: true,
                    pageSize: 999
                });
                dataview.store.implicitModel = true;

                callback(cfg);
            });
        }
    },

    initEvents: function() {
        var me = this;

        me.callParent(arguments);

        me.ownerCt.on('beforeexpand', function() {
            var tourney = me.ownerCt.module.tourney;

            if(tourney.currentturn == 1 && tourney.rankedturn === 0) {
                me.setHeight(275);
                if(!me.competitorDrop) {
                    me.competitorDrop = new SoL.view.Boards.CompetitorDrop(me);
                }
                me.store.load();
            } else {
                me.setHeight(80);
                me.store.removeAll();
            }
        });
    },

    prepareData: function(data, index, record) {
        var me = this;
        var dirty = me.store.classifyRecord(record);

        me.callParent(data, index, record);

        data.dirtyCls = dirty === '' ? '' : ' '+dirty;
        return data;
    },

    commitChanges: function(callback, scope) {
        var me = this;

        me.store.commitChanges('/bio/saveChanges',
                               me.store.proxy.reader.idProperty,
                               function() {
                                   me.ownerCt.module.reloadMatches();
                                   if(callback) {
                                       callback();
                                   }
                               }, scope);
    },

    resetChanges: function() {
        var me = this;

        me.store.rejectChanges();
        me.refresh();
    }
});


Ext.define('SoL.view.Boards.CompetitorDrop', {
    extend: 'Ext.dd.DropTarget',
    uses: ['MP.window.Notification'],

    group: 'competitor',

    constructor: function(view) {
        var me = this;

        me.callParent([view.el, {}]);
        me.store = view.store;
        me.dataview = view;
        me.tourney = view.ownerCt.module.tourney;
    },

    notifyEnter: function(source, e, data) {
        var me = this;
        var r;

        if((r=me.notifyOver(source, e, data)) != me.dropNotAllowed) {
            me.callParent(source, e, data);
            return r;
        } else {
            return me.dropNotAllowed;
        }
    },

    notifyOver: function(source, e, data) {
        //jsl:unused source

        if(this.tourney.currentturn != 1 || this.tourney.rankedturn !== 0) {
            return this.dropNotAllowed;
        }

        var target = e.getTarget('.competitor', 10, true);
        if(!target) {
            return this.dropNotAllowed;
        }

        var tcontainer = target.parent();
        var targetId = parseInt(tcontainer.dom.attributes.mid.nodeValue, 10);

        return (target && targetId != data.sourceMatch.get("idmatch"))
            ? this.dropAllowed : this.dropNotAllowed;
    },

    notifyDrop : function(source, e, data) {
        //jsl:unused source

        if(this.tourney.currentturn != 1 && this.tourney.rankedturn === 0) {
            return false;
        }

        var target = e.getTarget('.competitor', 10, true);
        if(!target) {
            return false;
        }

        var tcontainer = target.parent();
        var targetId = parseInt(tcontainer.dom.attributes.mid.nodeValue, 10);
        var targetMatch = this.store.getById(targetId);
        var sourceMatch = data.sourceMatch;

        var ids;

        ids = String(data.sourceEl.id).split('_');
        var scomp = parseInt(ids[1],10);
        var idscomp = parseInt(ids[2],10);

        ids = String(target.id).split('_');
        var tcomp = parseInt(ids[1],10);
        var idtcomp = parseInt(ids[2],10);

        var sfullname = sourceMatch.get('competitor'+scomp+'FullName');

        if(scomp == 1 && !idtcomp) {
            sourceMatch.set('idcompetitor1',
                            data.sourceMatch.get('idcompetitor2'));
            sourceMatch.set('competitor1FullName',
                            data.sourceMatch.get('competitor2FullName'));
            sourceMatch.set('idcompetitor2', null);
            sourceMatch.set('competitor2FullName',
                            targetMatch.get('competitor'+tcomp+'FullName'));
        } else {
            sourceMatch.set('idcompetitor'+scomp, idtcomp);
            sourceMatch.set('competitor'+scomp+'FullName',
                            targetMatch.get('competitor'+tcomp+'FullName'));
        }

        if(!sourceMatch.get('idcompetitor2')) {
            if(!sourceMatch.get('score1')) {
                sourceMatch.set('score1', targetMatch.get('score1'));
            }
        }

        if(tcomp == 1 && !idscomp) {
            targetMatch.set('idcompetitor1',
                            targetMatch.get('idcompetitor2'));
            targetMatch.set('competitor1FullName',
                            targetMatch.get('competitor2FullName'));
            targetMatch.set('idcompetitor2', null);
            targetMatch.set('competitor2FullName', sfullname);
        } else {
            targetMatch.set('idcompetitor'+tcomp, idscomp);
            targetMatch.set('competitor'+tcomp+'FullName', sfullname);
        }

        if(!targetMatch.get('idcompetitor2')) {
            if(!targetMatch.get('score1')) {
                targetMatch.set('score1', sourceMatch.get('score1'));
            }

        }

        if(sourceMatch.get('idcompetitor2')) {
            sourceMatch.set('score1', 0);
        }

        if(targetMatch.get('idcompetitor2')) {
            targetMatch.set('score1', 0);
        }

        this.dataview.refresh();
        return true;
    }
});
