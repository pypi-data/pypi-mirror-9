//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- "save" and "restore" on the top toolbar
// :Creato:    lun 26 nov 2012 15:39:34 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/


Ext.define('MP.action.SaveAndResetOnToolbar', {
    extend: 'MP.action.Plugin',
    uses: ['MP.action.SaveAndReset'],

    attachActions: function() {
        var me = this, tbar;
        var sandr = MP.action.SaveAndReset;

        me.callParent();

        tbar = me.component.child('#ttoolbar');

        if(tbar) {
            var saction = me.component.findActionById(sandr.SAVE_ACTION);
            var raction = me.component.findActionById(sandr.RESTORE_ACTION);
            tbar.add('->');
            tbar.add(saction);
            tbar.add(raction);
        }
    }
});
