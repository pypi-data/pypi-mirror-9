/*!
 * Ext JS Library 4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/


/**
 * @class MP.desktop.Desktop
 * @extends Ext.panel.Panel
 * <p>This class manages the wallpaper, shortcuts and taskbar.</p>
 */
Ext.define('MP.desktop.Desktop', {
    extend: 'Ext.panel.Panel',

    alias: 'widget.desktop',

    uses: [
        'Ext.util.MixedCollection',
        'Ext.menu.Menu',
        'Ext.view.View', // dataview
        'Ext.window.Window',

        'MP.desktop.TaskBar',
        'MP.desktop.Wallpaper'
    ],

    activeWindowCls: 'mp-desktop-active-win',
    inactiveWindowCls: 'mp-desktop-inactive-win',
    lastActiveWindow: null,

    border: false,
    html: '&#160;',
    layout: 'fit',

    xTickSize: 1,
    yTickSize: 1,

    app: null,

    /**
     * @cfg {Array|Store} shortcuts
     * The items to add to the DataView. This can be a {@link Ext.data.Store Store} or a
     * simple array. Items should minimally provide the fields in the
     * {@link MP.desktop.ShorcutModel ShortcutModel}.
     */
    shortcuts: null,

    /**
     * @cfg {String} shortcutItemSelector
     * This property is passed to the DataView for the desktop to select shortcut items.
     * If the {@link #shortcutTpl} is modified, this will probably need to be modified as
     * well.
     */
    shortcutItemSelector: 'div.mp-desktop-shortcut',

    /**
     * @cfg {String} shortcutTpl
     * This XTemplate is used to render items in the DataView. If this is changed, the
     * {@link shortcutItemSelect} will probably also need to changed.
     */
    shortcutTpl: [
        '<tpl for=".">',
            '<div class="mp-desktop-shortcut" id="{name}-shortcut">',
                '<div class="mp-desktop-shortcut-icon {iconCls}">',
                    '<img src="',Ext.BLANK_IMAGE_URL,'" title="{name}">',
                '</div>',
                '<span class="mp-desktop-shortcut-text">{name}</span>',
            '</div>',
        '</tpl>',
        '<div class="x-clear"></div>'
    ],

    /**
     * @cfg {Object} taskbarConfig
     * The config object for the TaskBar.
     */
    taskbarConfig: null,

    /**
     * @cfg {String} wallpaper
     * The URL of the background image.
     */
    wallpaper: null,

    /**
     * @cfg {String} wallpaperStyle
     * The style of the wallpaper, either the string "center", or
     * "tile" or "stretch".
     */
    wallpaperStyle: null,

    windowMenu: null,

    initComponent: function () {
        var me = this;

        me.windowMenu = new Ext.menu.Menu(me.createWindowMenu());

        me.bbar = me.taskbar = new MP.desktop.TaskBar(me.taskbarConfig);
        me.taskbar.windowMenu = me.windowMenu;

        me.windows = new Ext.util.MixedCollection();

        me.contextMenu = new Ext.menu.Menu(me.createDesktopMenu());

        me.items = [
            { xtype: 'wallpaper',
              id: me.id+'_wallpaper',
              style: me.wallpaperStyle },
            me.createDataView()
        ];

        me.callParent();

        me.shortcutsView = me.items.getAt(1);
        me.shortcutsView.on('itemclick', me.onShortcutItemClick, me);

        var wallpaper = me.wallpaper;
        me.wallpaper = me.items.getAt(0);
        if (wallpaper) {
            me.setWallpaper(wallpaper, me.wallpaperStyle);
        }
    },

    afterRender: function () {
        var me = this;
        me.callParent();
        me.el.on('contextmenu', me.onDesktopMenu, me);
    },

    //------------------------------------------------------
    // Overrideable configuration creation methods

    createDataView: function () {
        var me = this;
        return {
            xtype: 'dataview',
            overItemCls: 'x-view-over',
            trackOver: true,
            itemSelector: me.shortcutItemSelector,
            store: me.shortcuts,
            style: {
                position: 'absolute'
            },
            x: 0, y: 0,
            tpl: new Ext.XTemplate(me.shortcutTpl)
        };
    },

    createDesktopMenu: function () {
        var me = this, ret = {
            items: me.contextMenuItems || []
        };

        if (ret.items.length) {
            ret.items.push('-');
        }

        ret.items.push(
                { text: _('Tile'), handler: me.tileWindows, scope: me, minWindows: 1 },
                { text: _('Cascade'), handler: me.cascadeWindows, scope: me, minWindows: 1 });

        return ret;
    },

    createWindowMenu: function () {
        var me = this;
        return {
            defaultAlign: 'br-tr',
            items: [
                { text: _('Restore'), handler: me.onWindowMenuRestore, scope: me },
                { text: _('Minimize'), handler: me.onWindowMenuMinimize, scope: me },
                { text: _('Maximize'), handler: me.onWindowMenuMaximize, scope: me },
                '-',
                { text: _('Close'), handler: me.onWindowMenuClose, scope: me }
            ],
            listeners: {
                beforeshow: me.onWindowMenuBeforeShow,
                hide: me.onWindowMenuHide,
                scope: me
            }
        };
    },

    //------------------------------------------------------
    // Event handler methods

    onDesktopMenu: function (e) {
        var me = this, menu = me.contextMenu;
        e.stopEvent();
        if (!menu.rendered) {
            menu.on('beforeshow', me.onDesktopMenuBeforeShow, me);
        }
        menu.showAt(e.getXY());
        menu.doConstrain();
    },

    onDesktopMenuBeforeShow: function (menu) {
        var me = this, count = me.windows.getCount();

        menu.items.each(function (item) {
            var min = item.minWindows || 0;
            item.setDisabled(count < min);
        });
    },

    onShortcutItemClick: function (dataView, record) {
        //jsl:unused dataView
        var me = this, module = me.app.getModule(record.data.moduleId);

        if (module) {
            module.createOrShowWindow();
        }
    },

    onWindowClose: function(win) {
        var me = this;
        me.windows.remove(win);
        me.taskbar.removeTaskButton(win.taskButton);
        me.updateActiveWindow();
    },

    //------------------------------------------------------
    // Window context menu handlers

    onWindowMenuBeforeShow: function (menu) {
        var items = menu.items.items, win = menu.theWin;
        items[0].setDisabled(win.maximized !== true && win.hidden !== true); // Restore
        items[1].setDisabled(win.minimized === true); // Minimize
        items[2].setDisabled(win.maximized === true || win.hidden === true); // Maximize
    },

    onWindowMenuClose: function () {
        var me = this, win = me.windowMenu.theWin;

        win.close();
    },

    onWindowMenuHide: function (menu) {
        Ext.defer(function() {
            menu.theWin = null;
        }, 1);
    },

    onWindowMenuMaximize: function () {
        var me = this, win = me.windowMenu.theWin;

        win.maximize();
        win.toFront();
    },

    onWindowMenuMinimize: function () {
        var me = this, win = me.windowMenu.theWin;

        win.minimize();
    },

    onWindowMenuRestore: function () {
        var me = this, win = me.windowMenu.theWin;

        me.restoreWindow(win);
    },

    //------------------------------------------------------
    // Dynamic (re)configuration methods

    getWallpaper: function () {
        return this.wallpaper.wallpaper;
    },

    setTickSize: function(xTickSize, yTickSize) {
        var me = this,
            xt = me.xTickSize = xTickSize,
            yt = me.yTickSize = (arguments.length > 1) ? yTickSize : xt;

        me.windows.each(function(win) {
            var dd = win.dd, resizer = win.resizer;
            dd.xTickSize = xt;
            dd.yTickSize = yt;
            resizer.widthIncrement = xt;
            resizer.heightIncrement = yt;
        });
    },

    setWallpaper: function (wallpaper, style) {
        this.wallpaper.setWallpaper(wallpaper, style);
        return this;
    },

    //------------------------------------------------------
    // Window management methods

    cascadeWindows: function() {
        var x = 0, y = 0,
            zmgr = this.getDesktopZIndexManager();

        zmgr.eachBottomUp(function(win) {
            if (win.isWindow && win.isVisible() && !win.maximized) {
                win.setPosition(x, y);
                x += 20;
                y += 20;
            }
        });
    },

    /**
     * Constrain `width` and `height` to fit the current size of the
     * desktop, leaving some free space around the window.
     * The input parameters are optional: width is by default 800 and
     * height 640.
     * If given, the third parameter is a string that indicates the
     * alignment of window: "N" for North, "S" for South, "W" for
     * West, "E" for East, as well as the usual intermediary points
     * such as "NW", "NE", "SW" and "SE".
     * Return a dictionary with the two constrained dimensions and
     * eventually the horizontal and vertical offsets, `x` and `y`.
     */
    getReasonableWindowSize: function(width, height, align) {
        var me = this;
        var desktop_width = me.getWidth(true);
        var desktop_height = me.getHeight(true) - me.taskbar.getHeight();
        var max_width, max_height, result;

        if(width === undefined) {
            width = 800;
        }
        if(height === undefined) {
            height = 640;
        }

        max_width = desktop_width;
        if(max_width > 1600) {
            max_width = 1024;
        } else if (max_width > 1024) {
            max_width = 800;
        } else {
            max_width -= 40;
        }

        max_height = desktop_height;
        if(max_height > 1024) {
            max_height = 800;
        } else if (max_height > 800) {
            max_height = 640;
        } else {
            max_height -= 40;
        }

        result = {
            width: width < max_width ? width : max_width,
            height: height < max_height ? height : max_height
        };

        if(align) {
            switch(align) {
            case 'N':
                result.y = 10;
                break;
            case 'S':
                result.y = desktop_height - result.height - 10;
                break;
            case 'W':
                result.x = 10;
                break;
            case 'E':
                result.x = desktop_width - result.width - 10;
                break;
            case 'NW':
                result.x = 10;
                result.y = 10;
                break;
            case 'NE':
                result.x = desktop_width - result.width - 10;
                result.y = 10;
                break;
            case 'SW':
                result.x = 10;
                result.y = desktop_height - result.height - 10;
                break;
            case 'SE':
                result.x = desktop_width - result.width - 10;
                result.y = desktop_height - result.height - 10;
                break;
            default:
                break;
            }
        }

        return result;
    },

    createWindow: function(config, cls) {
        var me = this, win, cfg = Ext.applyIf(config || {}, {
            stateful: false,
            isWindow: true,
            constrainHeader: true,
            minimizable: true,
            maximizable: true,
            layout: 'fit',
            animCollapse: false,
            onEsc: Ext.emptyFn
        });

        cls = cls || Ext.window.Window;
        win = me.add(new cls(cfg));

        me.windows.add(win);

        win.taskButton = me.taskbar.addTaskButton(win);
        win.animateTarget = win.taskButton.el;

        win.on({
            activate: me.updateActiveWindow,
            beforeshow: me.updateActiveWindow,
            deactivate: me.updateActiveWindow,
            minimize: me.minimizeWindow,
            destroy: me.onWindowClose,
            scope: me
        });

        win.on({
            boxready: function () {
                win.dd.xTickSize = me.xTickSize;
                win.dd.yTickSize = me.yTickSize;

                if (win.resizer) {
                    win.resizer.widthIncrement = me.xTickSize;
                    win.resizer.heightIncrement = me.yTickSize;
                }
            },
            single: true
        });

        // Replace normal window close w/fadeOut animation
        win.doClose = function () {
            win.doClose = Ext.emptyFn; // dblclick can call again...
            win.el.disableShadow();
            win.el.fadeOut({
                listeners: {
                    afteranimate: function () {
                        win.destroy();
                    }
                }
            });
        };

        // Rectify double click on header behaviour, to fit only the
        // vertical dimension
        win.toggleMaximize = function() {
            if(!this.maximized) {
                var curpos = win.getPosition(true);
                var cursize = win.getSize();
                var vs = win.container.getViewSize();
                win.setPosition(curpos[0],0);
                win.setSize(cursize.width, vs.height - me.taskbar.getHeight());
            }
        };

        return win;
    },

    getActiveWindow: function () {
        var win = null,
            zmgr = this.getDesktopZIndexManager();

        if (zmgr) {
            // We cannot rely on activate/deactive because that fires against non-Window
            // components in the stack.

            zmgr.eachTopDown(function (comp) {
                if (comp.isWindow && !comp.hidden) {
                    win = comp;
                    return false;
                }
                return true;
            });
        }

        return win;
    },

    getDesktopZIndexManager: function () {
        var windows = this.windows;
        // TODO - there has to be a better way to get this...
        return (windows.getCount() && windows.getAt(0).zIndexManager) || null;
    },

    getWindow: function(id) {
        return this.windows.get(id);
    },

    minimizeWindow: function(win) {
        win.minimized = true;
        win.hide();
    },

    restoreWindow: function (win) {
        if (win.isVisible()) {
            win.restore();
            win.toFront();
        } else {
            win.show();
        }
        return win;
    },

    tileWindows: function() {
        var me = this, availWidth = me.body.getWidth(true);
        var x = me.xTickSize, y = me.yTickSize, nextY = y;

        me.windows.each(function(win) {
            if (win.isVisible() && !win.maximized) {
                var w = win.el.getWidth();

                // Wrap to next row if we are not at the line start and this Window will
                // go off the end
                if (x > me.xTickSize && x + w > availWidth) {
                    x = me.xTickSize;
                    y = nextY;
                }

                win.setPosition(x, y);
                x += w + me.xTickSize;
                nextY = Math.max(nextY, y + win.el.getHeight() + me.yTickSize);
            }
        });
    },

    updateActiveWindow: function () {
        var me = this, activeWindow = me.getActiveWindow(), last = me.lastActiveWindow;
        if (activeWindow === last) {
            return;
        }

        if (last) {
            if (last.el && last.el.dom) {
                last.addCls(me.inactiveWindowCls);
                last.removeCls(me.activeWindowCls);
            }
            last.active = false;
        }

        me.lastActiveWindow = activeWindow;

        if (activeWindow) {
            activeWindow.addCls(me.activeWindowCls);
            activeWindow.removeCls(me.inactiveWindowCls);
            activeWindow.minimized = false;
            activeWindow.active = true;
        }

        me.taskbar.setActiveButton(activeWindow && activeWindow.taskButton);
    }
});
