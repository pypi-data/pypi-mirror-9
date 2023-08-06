//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Standard "save" and "restore" actions.
// :Creato:    lun 26 nov 2012 15:36:14 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/

Ext.define('MP.action.SaveAndReset', {
    extend: 'MP.action.StoreAware',
    uses: ['Ext.Action'],

    statics: {
        SAVE_ACTION: 'save',
        RESTORE_ACTION: 'restore'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        var target = me.component;

        me.saveAction = me.addAction(new Ext.Action({
            itemId: ids.SAVE_ACTION,
            disabled: true,
            text: _('Save'),
            tooltip: _('Confirm the changes.'),
            iconCls: 'mp-save-action-icon',
            needsValidState: true,
            needsDirtyState: true,
            handler: function(options) {
                var callback = options && options.callback || null;
                var scope = options && options.scope || null;
                target.commitChanges(callback, scope);
            }
        }));

        me.restoreAction = me.addAction(new Ext.Action({
            itemId: ids.RESTORE_ACTION,
            disabled: true,
            text: _('Restore'),
            tooltip: _('Rollback the changes.'),
            iconCls: 'mp-restore-action-icon',
            needsDirtyState: true,
            handler: function() {
                target.resetChanges();
            }
        }));
    }
});
