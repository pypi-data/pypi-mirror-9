/*!
 * Ext JS Library 4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */

/*jsl:declare Ext*/

/**
 * @class MP.desktop.Wallpaper
 * @extends Ext.Component
 * <p>This component renders an image that stretches to fill the component.</p>
 */
Ext.define('MP.desktop.Wallpaper', {
    extend: 'Ext.Component',

    alias: 'widget.wallpaper',

    cls: 'mp-desktop-wallpaper',
    html: '<img src="'+Ext.BLANK_IMAGE_URL+'">',

    style: null,
    wallpaper: null,
    stateful: true,
    stateId: 'desk-wallpaper',

    afterRender: function () {
        var me = this;
        me.callParent();
        me.setWallpaper(me.wallpaper, me.style);
    },

    applyState: function () {
        var me = this, old = me.wallpaper;
        me.callParent(arguments);
        if (old != me.wallpaper) {
            me.setWallpaper(me.wallpaper, me.style);
        }
    },

    getState: function () {
        return this.wallpaper && {
            wallpaper: this.wallpaper,
            style: this.style
        };
    },

    setWallpaper: function (wallpaper, style) {
        var me = this, imgEl, bkgnd;

        if(style) {
            me.style = style;
        }
        me.wallpaper = wallpaper;

        if (me.rendered) {
            imgEl = me.el.dom.firstChild;

            if (!wallpaper || wallpaper == Ext.BLANK_IMAGE_URL) {
                Ext.fly(imgEl).hide();
            } else if (me.style == 'stretch') {
                imgEl.src = wallpaper;

                me.el.removeCls(['mp-desktop-wallpaper-tiled',
                                 'mp-desktop-wallpaper-centered']);
                Ext.fly(imgEl).setStyle({
                    width: '100%',
                    height: '100%'
                }).show();
            } else if (me.style == 'center') {
                Ext.fly(imgEl).hide();

                bkgnd = 'url('+wallpaper+')';
                me.el.removeCls('mp-desktop-wallpaper-tiled');
                me.el.addCls('mp-desktop-wallpaper-centered');
            } else /* if (me.style == 'tile') */ {
                Ext.fly(imgEl).hide();

                bkgnd = 'url('+wallpaper+')';
                me.el.removeCls('mp-desktop-wallpaper-centered');
                me.el.addCls('mp-desktop-wallpaper-tiled');
            }

            me.el.setStyle({
                backgroundImage: bkgnd || ''
            });
            if(me.stateful) {
                me.saveState();
            }
        }
        return me;
    }
});
