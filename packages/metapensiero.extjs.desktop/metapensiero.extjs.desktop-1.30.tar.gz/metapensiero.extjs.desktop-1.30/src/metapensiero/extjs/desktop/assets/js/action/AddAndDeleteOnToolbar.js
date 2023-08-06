//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- "add" and "delete" on the top toolbar
// :Creato:    lun 26 nov 2012 15:44:50 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/

Ext.define('MP.action.AddAndDeleteOnToolbar', {
    extend: 'MP.action.Plugin',
    uses: ['MP.action.AddAndDelete'],

    attachActions: function() {
        var me = this, tbar;
        var addndel = MP.action.AddAndDelete;

        me.callParent();

        tbar = me.component.child('#ttoolbar');

        if(tbar) {
            var anaction = me.component.findActionById(addndel.ADD_ACTION);
            var draction = me.component.findActionById(addndel.DELETE_ACTION);
            tbar.add(0, anaction);
            tbar.add(1, draction);
        }
    }
});
