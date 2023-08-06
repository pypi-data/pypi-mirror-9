//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop --
// :Creato:    lun 26 nov 2012 17:29:05 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/


Ext.define('MP.action.ModifyDetails', {
    extend: 'MP.action.StoreAware',
    uses: ['Ext.Action'],

    statics: {
        MODIFY_DETAILS_ACTION: 'modify_details'
    },

    /**
     * @cfg {Function} getMasterGrid
     * A function that returns the reference grid.
     */
    getMasterGrid: Ext.emptyFn,

    /**
     * @cfg {Function} createDetailsWindow
     * A function that will called with the selected record as the
     * only argument and should create its detail view.
     */
    createDetailsWindow: Ext.emptyFn,

    initActions: function() {
        var me = this;

        me.callParent();

        me.modifyDetailsAction = me.addAction(new Ext.Action({
            itemId: me.statics().MODIFY_DETAILS_ACTION,
            text: _('Modify'),
            tooltip: _('Modify details of the selected record.'),
            iconCls: 'mp-modify-action-icon',
            needsOneSelectedRow: true,
            disabled: true,
            handler: function() {
                var mg = me.getMasterGrid();
                var record = mg.getSelectionModel().getSelection()[0];
                me.createDetailsWindow(record);
            }
        }));

    },

    attachActions: function() {
        var me = this;
        var mg = me.getMasterGrid();

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        if(tbar) {
            tbar.add(2, '-');
            tbar.add(3, me.modifyDetailsAction);
        }

        mg.on({
            itemdblclick: function() {
                var action = me.modifyDetailsAction;
                if(!action.isDisabled()) {
                    action.execute();
                }
            }
        });
    }
});
