//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Basic grid
// :Creato:    mer 05 dic 2012 15:31:28 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/


Ext.define('MP.grid.Basic', {
    extend: 'MP.grid.Custom',

    uses: [
        'MP.action.SaveAndReset',
        'MP.action.SaveAndResetOnToolbar',
        'MP.grid.plugin.FilterBar',
        'MP.toolbar.Paging'
    ],

    alias: 'widget.basic-grid',

    /**
     * @cfg {Bool} noTopToolbar
     * Set it to true to disable the automatic creation of the top toolbar
     */
    noTopToolbar: false,

    /**
     * @cfg {Bool} noBottomToolbar
     * Set it to true to disable the automatic creation of the bottom
     * paging toolbar
     */
    noBottomToolbar: false,

    /**
     * @cfg {Bool} noFilterbar
     * Set it to true to disable the automatic creation of the filter
     * bar
     */
    noFilterbar: false,

    /**
     * @cfg {Number} clicksToEdit
     * Number of clicks needed to trigger the cell editor. Possible
     * values are 0, to completely disable the cell editing plugin, 1
     * or 2.
     */
    clicksToEdit: 2,

    /**
     * @cfg {Bool} noSaveAndResetActions
     * Set it to true to disable the save and reset actions.
     */

    initComponent: function() {
        var me = this;

        if(!me.noFilterbar) {
            var filterbarplugin = {
                ptype: 'filterbar',
                showShowHideButton: true,
                showClearAllButton: true
            };

            if(Ext.isArray(me.plugins)) {
                me.plugins.unshift(filterbarplugin);
            } else {
                me.plugins = [filterbarplugin];
            }
        }

        if(!me.readOnly && !me.noSaveAndResetActions) {
            var sractions = Ext.create('MP.action.SaveAndReset');
            var sbplugin = Ext.create('MP.action.SaveAndResetOnToolbar');

            if(Ext.isArray(me.plugins)) {
                me.plugins.unshift(sractions, sbplugin);
            } else {
                me.plugins = [sractions, sbplugin];
            }
        }

        var ditems = [];

        if(!me.noTopToolbar) {
            ditems.push({
                xtype: 'toolbar',
                dock: 'top',
                itemId: 'ttoolbar'
            });
        }

        if(!me.noBottomToolbar) {
            ditems.push(Ext.create('MP.toolbar.Paging', {
                dock: 'bottom',
                displayInfo: true,
                itemId: 'ptoolbar'
            }));
        }

        if(ditems.length>0) {
            if(Ext.isArray(me.dockedItems)) {
                me.dockedItems.push(ditems);
            } else {
                me.dockedItems = ditems;
            }
        }

        me.callParent();

        if(!me.noBottomToolbar) {
            var toolbar = me.child('#ptoolbar');
            var sizeitem = toolbar.child('#sizeItem');

            if(me.store && me.store.storeId != 'ext-empty-store') {
                toolbar.bindStore(me.store);
            } else {
                me.on('reconfigure', function(grid, store) {
                    //jsl:unused grid
                    toolbar.bindStore(store);
                });
            }

            // recompute ideal pagesize by double clicking on the page size
            sizeitem.on('render', function(c) {
                c.getEl().on({
                    dblclick: function() {
                        var s = me.store;
                        var anode = me.view.getNode(0);
                        var gridh = me.view.getHeight();
                        var rowh, pagesize;

                        if(anode) {
                            rowh = Ext.fly(anode).getHeight()+1;
                        } else {
                            rowh = 22;
                        }
                        pagesize = Math.floor(gridh / rowh);
                        if(pagesize != s.pageSize) {
                            var firstrec = s.pageSize * (s.currentPage - 1) + 1;
                            var newpage = Math.ceil(firstrec / pagesize);
                            s.pageSize = pagesize;
                            sizeitem.setValue(pagesize);
                            s.loadPage(newpage);
                        }
                    }
                });
            });
        }
    }
});
