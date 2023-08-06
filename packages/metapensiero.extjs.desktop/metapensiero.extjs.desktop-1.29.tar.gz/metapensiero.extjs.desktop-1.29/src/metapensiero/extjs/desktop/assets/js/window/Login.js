//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Login window
// :Creato:    mar 31 lug 2012 23:37:58 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare __title__*/
/*jsl:declare __version__*/


Ext.define('MP.form.StandaloneLabel', {
    extend: 'Ext.form.Label',
    alias: 'widget.standalone-label',

    /**
     * Override the Label's behaviour that always inserts a “for”
     * attribute, eventually empty, even if its documentation says it
     * should not. This causes a “getElementById() called with an
     * empty string” warning in Firebug console.
     */
    getElConfig: function() {
        var me = this;

        me.html = me.text ? Ext.util.Format.htmlEncode(me.text) : (me.html || '');
        return Ext.form.Label.superclass.getElConfig.apply(me);
    }
});


Ext.define('MP.window.Login', {
    extend: 'Ext.Window',
    alias: 'widget.loginwindow',
    requires: 'MP.form.StandaloneLabel',
    uses: 'Ext.form.Panel',

    title: _('Please login'),
    titleAlign: 'center',
    width: 400,
    autoHeight: true,
    closable: false,
    resizable: false,
    draggable: false,
    layout: 'fit',
    border: false,
    modal: true,

    initComponent: function() {
        var me = this;

        Ext.apply(me, {
            items: [{
                xtype: 'form',
                plain: true,
                frame: true,
                border: 0,
                bodyPadding: 5,

                url: '/auth/login',

                items: me.getFormFields()
            }]
        });
        me.callParent();
    },

    buttons: [{
        xtype: 'standalone-label',
        text: __title__ + ' ' + __version__
    }, '->', {
        text: _("Login"),
        type: "submit",
        action: "login",
        formBind: true
    }],

    defaultFocus: 'username',

    /**
     * Return the array of fields/items to build the login form.
     * This implementation setups the standard “username” and
     * “password” fields. Subclasses can tweak the array as needed,
     * for example adding a logo:
     *
     *   getFormFields: function() {
     *       var fields = this.callParent();
     *       fields.unshift({
     *           xtype: 'image',
     *           src: '/static/images/logo.png',
     *           style: 'margin-left: 84px;',
     *           width: 212,
     *           height: 85
     *       });
     *       return fields;
     *   }
     */
    getFormFields: function() {
        return [{
            itemId: 'username',
            xtype: 'textfield',
            fieldLabel: _('Username'),
            name: 'username',
            allowBlank: false,
            anchor: '100%',
            selectOnFocus: true
        }, {
            xtype: 'textfield',
            fieldLabel: _('Password'),
            name: 'password',
            allowBlank: false,
            inputType: 'password',
            anchor: '100%',
            selectOnFocus: true
        }];
    }
});
