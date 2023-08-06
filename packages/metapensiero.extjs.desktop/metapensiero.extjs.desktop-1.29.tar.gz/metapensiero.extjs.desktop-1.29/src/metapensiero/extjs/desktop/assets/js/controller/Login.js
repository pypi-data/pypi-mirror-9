//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Basic login controller
// :Creato:    mar 31 lug 2012 23:33:44 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare document*/
/*jsl:declare _*/
/*jsl:declare MP*/


Ext.define('MP.controller.Login', {
    extend: 'Ext.app.Controller',

    uses: [
        'MP.data.MetaData',
        'MP.desktop.App'
    ],

    /**
     * @cfg {String} applicationClass
     * The class used to instantiate the main application object, by
     * default “MP.desktop.App”.
     */

    init: function() {
        this.control({
            'loginwindow textfield': {
                specialkey: this.keyenter
            },
            'loginwindow button[action=login]': {
                click: this.login
            }
        });
    },

    refs: [{
        ref: 'loginwindow',
        selector: 'loginwindow'
    }, {
        ref: 'loginbutton',
        selector: 'loginwindow button[action=login]'
    }],

    keyenter: function(field, e) {
        var value = field.getValue();

        if(e.getKey()===e.ENTER && !Ext.isEmpty(value)) {
            this.login(this.getLoginbutton());
        }
    },

    createUserDesktop: function(user) {
        var me = this;
        var dapp = Ext.create(me.applicationClass || 'MP.desktop.App', {
            user: user
        });

        dapp.on('ready', function() {
            var win = me.getLoginwindow();
            win.down('form').getEl().unmask();
            win.hide();
        });
        dapp.on('logout', function() {
            var win = me.getLoginwindow();
            var panel = win.down('form');

            panel.getForm().reset();

            dapp.desktop.windows.each(function(w) {
                w.destroy();
            });

            dapp.desktop.hide();
            dapp.desktop.destroy();

            MP.data.MetaData.clearCache();

            //<debug>
            if(dapp.user.is_admin) {
                me.sendLoaderHistory();
            }
            //</debug>

            win.show();
        });

        return dapp;
    },

    //<debug>
    sendLoaderHistory: function() {
        var href = document.location.href;
        var hreflen = href.length;
        var sheets = document.styleSheets;
        var styles = [];

        for(var len=sheets.length, i=0; i<len; i++) {
            var url = sheets[i].href;
            // Do not consider inline stylesheets
            if(url) {
                if(hreflen && url.substring(0, hreflen) === href) {
                    url = url.substring(hreflen-1);
                }
                styles.push(url);
            }
        }

        Ext.Ajax.request({
            url: '/scripts',
            method: 'POST',
            params: {
                styles: Ext.encode(styles)
            }
        });
    },
    //</debug>

    login: function(button) {
        var me = this;
        var panel = button.up('window').down('form');
        var form = panel.getForm();

        if(form.isValid()) {
            panel.getEl().mask(_("Authentication..."));

            form.submit({
                success: function(f, a) {
                    //jsl:unused f
                    var user = a.result;

                    me.createUserDesktop(user);
                },

                failure: function(f, a) {
                    f.owner.el.unmask();
                    Ext.Msg.alert(_('Error'),
                                  a.result
                                  ? a.result.message
                                  : _('No response from the server'));
                }
            });
        }
    }
});
