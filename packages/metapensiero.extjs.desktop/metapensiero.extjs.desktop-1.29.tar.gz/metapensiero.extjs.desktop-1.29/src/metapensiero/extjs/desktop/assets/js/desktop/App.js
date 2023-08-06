/*!
 * Ext JS Library 4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */

/*jsl:declare Ext*/
/*jsl:declare window*/
/*jsl:declare _*/

Ext.define('MP.desktop.App', {
    mixins: {
        observable: 'Ext.util.Observable'
    },

    requires: [
        'Ext.container.Viewport',
        'Ext.window.MessageBox',
        'Ext.util.Format'
    ],

    uses: [
        'Ext.util.Point', // this is never required, but used by ExtJS EventXxx
        'MP.desktop.ShortcutModel',
        'MP.desktop.Desktop',
        'MP.desktop.TrayClock'
    ],

    /**
     * @cfg {String} desktopClass
     * The class used to instantiate the desktop object, by default
     * “MP.desktop.Desktop”.
     */

    isReady: false,
    modules: null,
    useQuickTips: true,

    constructor: function (config) {
        var me = this;
        me.addEvents(
            'ready',
            'beforeunload'
        );

        me.mixins.observable.constructor.call(this, config);

        if (Ext.isReady) {
            Ext.Function.defer(me.init, 10, me);
        } else {
            Ext.onReady(me.init, me);
        }
    },

    init: function() {
        var me = this, desktopCfg;

        if (me.useQuickTips) {
            Ext.QuickTips.init();
        }

        me.modules = me.getModules();

        desktopCfg = me.getDesktopConfig();
        me.desktop = Ext.create(me.desktopClass || 'MP.desktop.Desktop',
                                desktopCfg);

        me.viewport = Ext.create('Ext.container.Viewport', {
            layout: 'fit',
            items: [ me.desktop ]
        });

        Ext.EventManager.on(window, 'beforeunload', me.onUnload, me);

        me.isReady = true;
        me.fireEvent('ready', me);

        this.addEvents('logout');
    },

    /**
     * This method returns the configuration object for the context
     * menu of the Desktop object (by default an empty array).  A
     * derived class can override this method, returning an array of
     * menu configuration items, for example:
     *
     *  getContextMenuItems: function() {
     *      var me = this;
     *      return [{
     *          text: _('Change Settings'),
     *          handler: me.onSettings,
     *          scope: me
     *      }];
     *  }
     */
    getContextMenuItems: function() {
        return [];
    },

    /**
     * This method returns the configuration object for the Desktop object. A derived
     * class can override this method, call the base version to build the config and
     * then modify the returned object before returning it.
     */
    getDesktopConfig: function () {
        var me = this, cfg = {
            app: me,
            taskbarConfig: me.getTaskbarConfig(),
            contextMenuItems: me.getContextMenuItems(),
            shortcuts: Ext.create('Ext.data.Store', {
                model: 'MP.desktop.ShortcutModel',
                data: me.user.shortcuts || []
            })
        };

        return Ext.apply(cfg, me.desktopConfig);
    },

    getModules : function() {
        var me = this, modules = [];

        Ext.each(me.user.modules, function (module) {
            modules.push(Ext.create(module, {app: me}));
        });

        return modules;
    },

    /**
     * This method returns the configuration object for the tools
     * section of the Start Button, by default with a single item, the
     * logout button. A derived class can override this method, call
     * the base version to build the config and then modify the
     * returned object before returning it.
     */
    getToolConfig: function() {
        var me = this;

        return {
            width: 100,
            items: [{
                text: _('Logout'),
                tooltip: _('Terminate the application.'),
                iconCls: 'logout',
                handler: me.onLogout,
                scope: me
            }]
        };
    },

    /**
     * This method returns the configuration object for the Start Button. A derived
     * class can override this method, call the base version to build the config and
     * then modify the returned object before returning it.
     */
    getStartConfig: function () {
        var me = this, menu, launcher, cfg = {
            app: me,
            menu: [],
            title: me.user.fullname,
            iconCls: me.user.is_admin ? 'admin'
                : me.user.is_manager ? 'manager' : 'user',
            height: 300,
            toolConfig: me.getToolConfig()
        };

        Ext.apply(cfg, me.startConfig);

        Ext.each(me.modules, function (module) {
            launcher = module.launcher;
            if (launcher) {
                var orighandler = launcher.handler;
                if (!orighandler) {
                    orighandler = module.createOrShowWindow;
                }
                // Introduce an indirection, because the menu item
                // will pass itself and the event as argument to its
                // handler, which are pretty useless in our case,
                // and complicates argument handling in module's
                // createOrShowWindow since it may be called from
                // other places, such as a shortcuts, or directly from
                // user code, passing specific parameters
                launcher.handler = function() {
                    orighandler.call(module);
                };

                menu = cfg.menu;
                if(module.launcherPath) {
                    var paths = module.launcherPath.split('/');

                    for(var i=0, npaths=paths.length; i<npaths; i++) {
                        var pchunk = paths[i];
                        var submenu = null;

                        for(var j=0, jlen=menu.length; j<jlen; j++) {
                            if(menu[j].text === pchunk) {
                                submenu = menu[j].menu;
                                break;
                            }
                        }

                        if(!submenu) {
                            submenu = {
                                handler: Ext.emptyFn,
                                iconCls: 'submenu',
                                menu: [],
                                text: paths[i]
                            };
                            menu.push(submenu);
                            menu = submenu.menu;
                        } else {
                            menu = submenu;
                        }
                    }
                }
                menu.push(module.launcher);
            }
        });

        return cfg;
    },

    /**
     * This method returns the configuration object for the TaskBar. A derived class
     * can override this method, call the base version to build the config and then
     * modify the returned object before returning it.
     */
    getTaskbarConfig: function () {
        var me = this, cfg = {
            app: me,
            startConfig: me.getStartConfig(),
            quickStart: me.user.quickstart || [],
            trayItems: [
                { xtype: 'trayclock', flex: 1 }
            ]
        };

        return Ext.apply(cfg, me.taskbarConfig);
    },

    getModule: function(id) {
        var ms = this.modules;
        for (var i = 0, len = ms.length; i < len; i++) {
            var m = ms[i];
            if (m.id == id) {
                return m;
            }
        }
        return null;
    },

    onReady: function(fn, scope) {
        if (this.isReady) {
            fn.call(scope, this);
        } else {
            this.on({
                ready: fn,
                scope: scope,
                single: true
            });
        }
    },

    getDesktop: function() {
        return this.desktop;
    },

    onUnload: function(e) {
        if (this.fireEvent('beforeunload', this) === false) {
            e.stopEvent();
        }
    },

    onLogout: function () {
        var me = this;
        Ext.Msg.confirm(_('Terminate Session'),
                        _('Are you sure you want to logout?'),
                        function(bid) {
                            if(bid==='yes') {
                                var maskel = me.getDesktop().getEl();

                                maskel.mask('<span id="pbar"></span>');

                                var pbar = Ext.create('Ext.ProgressBar', {
                                    text: _("Please Wait..."),
                                    width: 180,
                                    renderTo: 'pbar',
                                    value: 1
                                });

                                Ext.Ajax.request({
                                    url: '/auth/logout',
                                    method: 'GET',
                                    success: function() {
                                        pbar.reset(true);
                                        maskel.unmask();
                                        me.fireEvent('logout', me);
                                    },
                                    failure: function(response) {
                                        pbar.reset(true);
                                        maskel.unmask();
                                        me.fireEvent('logout', me);
                                        console.error('Something went wrong: ', response);
                                    }
                                });
                            }
                        });
    }
});
