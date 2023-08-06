/*!
 * Ext JS Library 4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */

/*jsl:declare Ext*/
/*jsl:declare window*/
/*jsl:declare _*/

/**
 * @class MP.desktop.TrayClock
 * @extends Ext.toolbar.TextItem
 * This class displays a clock on the toolbar.
 */
Ext.define('MP.desktop.TrayClock', {
    extend: 'Ext.toolbar.TextItem',

    alias: 'widget.trayclock',

    cls: 'mp-desktop-trayclock',

    html: '&#160;',

    // TRANSLATORS: this is the format used to display current time in
    // the lower right corner of the desktop, see
    // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date for details
    // on the syntax.
    timeFormat: _('D d M, g:i A'),

    tpl: '{time}',

    initComponent: function () {
        var me = this;

        me.callParent();

        if (typeof(me.tpl) == 'string') {
            me.tpl = new Ext.XTemplate(me.tpl);
        }
    },

    afterRender: function () {
        var me = this;
        Ext.Function.defer(me.updateTime, 100, me);
        me.callParent();
    },

    onDestroy: function () {
        var me = this;

        if (me.timer) {
            window.clearTimeout(me.timer);
            me.timer = null;
        }

        me.callParent();
    },

    updateTime: function () {
        var me = this, time = Ext.Date.format(new Date(), me.timeFormat),
            text = me.tpl.apply({ time: time });
        if (me.lastText != text) {
            me.setText(text);
            me.lastText = text;
        }
        me.timer = Ext.Function.defer(me.updateTime, 10000, me);
    }
});
