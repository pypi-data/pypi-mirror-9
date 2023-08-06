/*!
 * Ext JS Library 4.0
 * Copyright(c) 2006-2011 Sencha Inc.
 * licensing@sencha.com
 * http://www.sencha.com/license
 */

/*jsl:declare Ext*/

/**
 * @class MP.desktop.ShortcutModel
 * @extends Ext.data.Model
 * This model defines the minimal set of fields for desktop shortcuts.
 */
Ext.define('MP.desktop.ShortcutModel', {
    extend: 'Ext.data.Model',
    requires: [
        // This seems strange but is really important: without this requirement the minificated
        // application fails with an error, maybe due to glitches in the ExtJS classes metadata
        'Ext.data.proxy.Ajax'
    ],
    fields: [
       { name: 'name' },
       { name: 'iconCls' },
       { name: 'moduleId' }
    ]
});
