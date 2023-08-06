/*!
 * Ext JS Library 4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare _*/


Ext.define('MP.desktop.Module', {
    extend: 'Ext.util.Observable',

    requires: [
        'MP.data.MetaData',
        'Ext.window.MessageBox'
    ],

    /**
     * @cfg {String} id
     * The unique id of this module, used by default also to identify
     * its main window.
     */

    /**
     * @cfg {String} iconCls
     * The CSS class used to associate the icon to the menu entry.
     */

    /**
     * @cfg {String or Function} launcherText
     * The text used for the menu entry. If this is null the module
     * won't appear in the menu. This may be also a function, to allow
     * lazy translation of the text: alternatively subclasses can simply
     * override the getLauncherText() method.
     */

    /**
     * @cfg {String or Function} launcherTooltip
     * The tooltip for the menu entry. This may be also a function, to allow
     * lazy translation of the text: alternatively subclasses can simply
     * override the getLauncherTooltip() method.
     */

    /**
     * @cfg {String} launcherPath
     * An optional '/'-separated sequence of submenu entries, used to
     * group launchers into submenus.
     */

    /**
     * @cfg {String} dataURL
     * The URL used to fetch data.
     */
    dataURL: null,

    /**
     * @cfg {Number} pageSize
     * Default number of records to fetch at once.
     */
    pageSize: 25,

    /**
     * @cfg {Object} app
     * The application instance.
     */

    constructor: function (config) {
        this.callParent([config]);
        this.init();
    },

    /**
     * If the window does not exist create it. In any case, show it.
     * Typically subclasses shall implement this method in this way:
     *
     *    createOrShowWindow: function() {
     *        var me = this;
     *        var desktop = me.app.getDesktop();
     *        var win = desktop.getWindow(me.id);
     *
     *        if(!win) {
     *            win = desktop.createWindow({...});
     *            win.show()
     *        } else {
     *            desktop.restoreWindow(win);
     *        }
     */
    createOrShowWindow: Ext.emptyFn,

    /**
     * Returns the launcher configuration for this module.
     * By default this is a plain menu entry, but subclasses may
     * generate arbitrary menu hierarchies by overriding this method,
     * for example:
     *
     *   createLauncher: function() {
     *       var me = this;
     *       var launcher = {
     *           handler: function() { return false; },
     *           text: "Submenu",
     *           tooltip: "Submenu test",
     *           menu: {
     *               items: [{
     *                   handler: me.createOrShowWindow,
     *                   scope: me,
     *                   iconCls: me.iconCls,
     *                   text: me.getLauncherText(),
     *                   tooltip: me.getLauncherTooltip()
     *               }, {
     *                   text: "Subsubmenu",
     *                   menu: {
     *                       items: [{
     *                           text: "Voice 1",
     *                           handler: me.createOrShowWindow
     *                       }, {
     *                           text: "Voice 2"
     *                       }]
     *                   }
     *               }
     *               ]
     *           }
     *       };
     *       return launcher;
     *   }
     */
    createLauncher: function() {
        var me = this, text = me.getLauncherText();

        if(text) {
            var tooltip = me.getLauncherTooltip();

            return {iconCls: me.iconCls, text: text, tooltip: tooltip};
        } else
            return null;
    },

    getLauncherText: function() {
        var me = this;
        var text = me.launcherText;

        if(typeof text == 'function')
            text = text.call(me);
        return text;
    },

    getLauncherTooltip: function() {
        var me = this;
        var tooltip = me.launcherTooltip;

        if(typeof tooltip == 'function')
            tooltip = tooltip.call(me);
        return tooltip;
    },

    init: function() {
        var me = this;
        me.launcher = me.createLauncher();
    },

    fetchFieldsAndColumns: function(callback, scope, url, overrides,
                             error_callback) {
        var me = this;

        MP.data.MetaData.fetch(url || me.dataURL, me, function(metadata) {
            callback.call(scope || me,
                          metadata.fields(overrides),
                          metadata.columns(overrides),
                          metadata.primary_key,
                          metadata.success_slot,
                          metadata.root_slot,
                          metadata.count_slot);
        }, error_callback);
    },

    /**
     * Helper function to execute an arbitrary sequence of functions,
     * and finally execute a callback, while showing a masked progress
     * bar.
     *
     * This is typically used within the createOrShowWindow() method like this:
     *
     *       me.configure(
     *           [me.getBuildingsConfig,
     *            me.getPadsConfig,
     *            me.getFloorsConfig,
     *            me.getRoomsConfig],
     *           function(done, config) {
     *               win = desktop.createWindow({
     *                   id: me.id,
     *                   title: me.getLauncherText(),
     *                   items: [
     *                       config.Buildings,
     *                       config.Pads,
     *                       config.Floors,
     *                       config.Rooms
     *                   ]
     *                   ...
     *               });
     *
     *               store.load({
     *                   params: {start: 0, limit: me.pageSize},
     *                   callback: function() {
     *                       win.on({show: done, single: true});
     *                       win.show();
     *                   }
     *               });
     *            }, {some_config: true});
     *
     * Each function is executed passing two callback functions, one
     * that should be called when everything goes well, the other when
     * an error occurs. In the latter case, the loop is terminated,
     * that is succeding functions won't be called at all. A third
     * argument is passed, the config object that each function may
     * alter as needed. This object is finally passed to the callback
     * function.
     *
     * @param {Function[]} functions The array of configuration functions
     * @param {Function} callback The workhorse function
     * @param {Object} config An object used to pass and collect
     * configuration options
     */
    configure: function(functions, callback, config) {
        var me = this;
        var maskel = me.app.getDesktop().getEl();
        var count = functions.length;
        var step = 1 / (count * 2 + 1);
        var value = 0;

        maskel.mask('<span id="pbar"></span>');

        var pbar = Ext.create('Ext.ProgressBar', {
            text: _("Initializing..."),
            width: 180,
            renderTo: 'pbar'
        });

        Ext.each(functions, function(f) {
            var keepgoing = true;

            value += step;
            pbar.updateProgress(value);
            f.call(me,
                   function() {
                       value += step;
                       pbar.updateProgress(value);
                       count--;
                       if(!count) {
                           value += step;
                           pbar.updateProgress(value);
                           callback.call(me, function() {
                               pbar.reset(true);
                               maskel.unmask();
                           }, config);
                       }
                   },
                   function() {
                       pbar.reset(true);
                       maskel.unmask();
                       keepgoing = false;
                   },
                   config);
            return keepgoing;
        });
    }
});
