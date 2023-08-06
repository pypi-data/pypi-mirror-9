//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- A paging toolbar with an additional "pageSize" input field.
// :Creato:    mer 05 dic 2012 15:43:08 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/


Ext.define('MP.toolbar.Paging', {
    extend: 'Ext.toolbar.Paging',

    uses: [
        'Ext.toolbar.*'
    ],

    getPagingItems: function() {
        var me = this;
        var items = me.callParent();

        items.unshift(
            _('Page size'),
            {
                xtype: 'numberfield',
                inputAttrTpl: ' data-qtip="'
                    + _('Double click to adjust the number to fit grid height.')
                    + '" ',
                itemId: 'sizeItem',
                name: 'sizeItem',
                cls: Ext.baseCSSPrefix + 'tbar-page-number',
                allowDecimals: false,
                minValue: 1,
                hideTrigger: true,
                enableKeyEvents: true,
                keyNavEnabled: false,
                selectOnFocus: true,
                submitValue: false,
                // mark it as not a field so the form will not catch
                // it when getting fields
                isFormField: false,
                width: me.inputItemWidth,
                margins: '-1 2 3 2',
                listeners: {
                    scope: me,
                    keydown: me.onPageSizeChange
                }
            },
            '-'
        );

        return items;
    },

    onPageSizeChange: function(field, e) {
        var me = this;
        var k = e.getKey();

        if(k == e.RETURN || k == e.TAB) {
            var v = field.getValue();
            var pagesize = parseInt(v, 10);
            var s = me.store;

            e.stopEvent();
            if(!v || isNaN(pagesize)) {
                field.setValue(me.pageSize);
            } else {
                if(pagesize != s.pageSize) {
                    var firstrec = s.pageSize * (s.currentPage - 1) + 1;
                    var newpage = Math.ceil(firstrec / pagesize);
                    s.pageSize = pagesize;
                    s.loadPage(newpage);
                }
            }
        }
    },

    bindStore: function(store) {
        this.callParent(arguments);
        if(store) {
            this.child('#sizeItem').setValue(store.pageSize);
        }
    }
});
