//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Standard editable grid
// :Creato:    dom 23 set 2012 17:56:02 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/


Ext.define('MP.grid.Panel', {
    extend: 'MP.grid.Editable',

    uses: ['MP.action.AddAndDeleteOnToolbar'],

    alias: 'widget.editable-grid',

    initComponent: function() {
        var me = this;

        me.callParent();

        if(!me.noAddAndDelete) {
            this.plugins.unshift(Ext.create('MP.action.AddAndDeleteOnToolbar'));
        }
    }
});
