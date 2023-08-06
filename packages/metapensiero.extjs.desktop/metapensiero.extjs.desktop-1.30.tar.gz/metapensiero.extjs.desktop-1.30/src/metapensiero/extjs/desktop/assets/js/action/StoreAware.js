//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Store aware actions factory
// :Creato:    lun 26 nov 2012 15:34:01 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/


Ext.define('MP.action.StoreAware', {
    extend: 'MP.action.Plugin',

    init: function(component) {
        var me = this;

        if(!me.shouldDisableAction) {
            if(component.shouldDisableAction) {
                me.shouldDisableAction =
                    component.shouldDisableAction.bind(component);
            } else {
                var store = component.store;

                if(store && store.storeId != 'ext-empty-store') {
                    if(store.shouldDisableAction) {
                        me.shouldDisableAction =
                            store.shouldDisableAction.bind(store);
                    }
                } else {
                    me.component.on('reconfigure', function(g, s) {
                        //jsl:unused g
                        if(s.shouldDisableAction) {
                            me.shouldDisableAction =
                                s.shouldDisableAction.bind(s);
                        }
                    });
                }
            }
        }
        me.callParent(arguments);
    },

    attachActions: function() {
        var me = this;
        var ua = function(/*store, record, action*/) {
            Ext.each(me.getActions(), me.updateAction, me);
        };

        me.callParent();

        var store = me.component.store;

        if(store && store.storeId != 'ext-empty-store') {
            store.on({
                scope: me,
                update: ua,
                load: ua,
                reject: ua,
                add: ua,
                datachanged: ua
            });
        } else {
            me.component.on('reconfigure', function(g, s) {
                //jsl:unused g
                s.on({
                    scope: me,
                    update: ua,
                    load: ua,
                    reject: ua,
                    add: ua,
                    datachanged: ua
                });
            });
        }

        if(me.component.getSelectionModel) {
            var sm = me.component.getSelectionModel();
            sm.on('selectionchange', ua, me);
        }
    }
});
