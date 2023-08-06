//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Custom grid
// :Creato:    mer 05 dic 2012 15:27:46 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare ngettext*/


Ext.define('MP.grid.Custom', {
    extend: 'Ext.grid.Panel',

    requires: [
        'MP.data.Store'
    ],

    uses: [
        'MP.data.MetaData',
        'Ext.data.proxy.Ajax'
    ],

    layout: 'fit',
    border: false,
    header: false,
    stateful: false,

    /**
     * @cfg {String} dataURL
     * Base URL to obtain data from the server.
     */
    dataURL: null,

    /**
     * @cfg {Object} extraParams
     * Extra parameters that will be included on every request.
     */

    /**
     * @cfg {String} saveChangesURL
     * URL to save changes back to the server. If not specified,
     * changes will be saved thru dataURL.
     */
    saveChangesURL: null,

    /**
     * @cfg {Object} metadataOverrides
     * When the grid is autoconfigured (no fields are specified) this
     * is used to possibly overrides metadata configurations.
     */

    /**
     * @cfg {String} idProperty
     * The name of the primary key.
     */
    idProperty: 'id',

    /**
     * @cfg {String} totalProperty
     * The name of the data slot containing the total count of records.
     */
    totalProperty: 'count',

    /**
     * @cfg {String} successProperty
     * The name of the data slot containing the success status.
     */
    successProperty: 'success',

    /**
     * @cfg {String} rootProperty
     * The name of the data slot containing the array of records.
     */
    rootProperty: 'root',

    /**
     * @cfg {Array} fields
     * An array with fields description.
     */
    fields: null,

    /**
     * @cfg {Array} columns An array with columns description
     */
    columns: null,

    /**
     * @cfg {Object} newRecordData
     * Used to initialize new records, may be a function.
     */
    newRecordData: null,

    /**
     * @cfg {Bool} remoteSort
     * Which kind of sort, remote by default.
     */
    remoteSort: true,

    /**
     * @cfg {Bool} storeAutoLoad
     * If storeAutoLoad is true or an Object, the store's load method is
     * automatically called after creation. If the value of storeAutoLoad
     * is an Object, this Object will be passed to the store's load
     * method.  Defaults to false.
     */
    storeAutoLoad: undefined,

    /**
     * @cfg {Ext.util.Sorter[]} sorters
     * Optional array of sorter objects. Only applies to 'read' actions.
     */
    sorters: undefined,

    /**
     * @cfg {Bool} remoteGroup
     * Which kind of grouping, local by default.
     */
    remoteGroup: false,

    /**
     * @cfg {String/Object[]} groupers
     * Either a string name of one of the fields in this Store's or an
     * Array of grouper configurations.
     */
    groupers: undefined,

    /**
     * @cfg {Object} filters
     * Initial filters for the store.
     */

    /**
     * @cfg {Object} stickyFilters
     * Initial sticky filters for the store.
     */

    /**
     * @cfg {Bool} autoShowAllEditors
     * Whether automatically show all editors on insert, true by default.
     */
    autoShowAllEditors: true,

    /**
     * @cfg {Bool} readOnly
     * When true, force readonly status on all columns.
     */

    /**
     * @cfg {Number} pageSize
     * By default 25, the number of records to show in a single page.
     */
    pageSize: 25,

    /**
     * @cfg {String} selType
     * The selection model for the grid, by default 'rowmodel'.
     */
    selType: 'rowmodel',

    /**
     * @cfg {Bool} immediateDeletions
     * Whether the grid should immediately commit deleted records or not.
     * This is particularly usefull when the grid has no “Save
     * changes” button.
     */

    /**
     * @cfg {Object[]} otherButtons
     * An array of additional buttons for the grid panel.
     */

    initComponent:function() {
        var me = this;

        if(!me.fields) {
            MP.data.MetaData.fetch(me.dataURL, me, me.configure);
        } else {
            if(!me.store) {
                me.store = me.createStore();
            }
        }

        if(me.otherButtons) {
            me.buttons = me.otherButtons.concat(me.buttons || []);
        }

        me.columns = {
            items: me.columns
        };

        me.callParent();
    },

    configure: function(metadata) {
        var me = this;
        var store;

        Ext.apply(me, {
            idProperty: metadata.primary_key,
            totalProperty: metadata.count_slot,
            successProperty: metadata.success_slot,
            rootProperty: metadata.root_slot
        });
        store = me.createStore(metadata);
        if(me.headerCt) {
            me.reconfigure(store, metadata.columns(me.metadataOverrides));
        } else {
            me.store = store;
            me.columns = metadata.columns(me.metadataOverrides);
        }
    },

    createStore: function(metadata) {
        var me = this;
        var model, store;
        var fields = metadata ? metadata.fields(me.overrides) : me.fields;

        model = Ext.define('MP.data.ImplicitModel-' + Ext.id(), {
            extend: 'Ext.data.Model',
            fields: fields,
            idProperty: me.idProperty
        });

        store = Ext.create('MP.data.Store', {
            model: model,
            pageSize: me.pageSize,
            proxy: {
                type: 'ajax',
                url: me.dataURL,
                extraParams: me.extraParams,
                reader: {
                    type: 'json',
                    idProperty: me.idProperty,
                    totalProperty: me.totalProperty,
                    successProperty: me.successProperty,
                    root: me.rootProperty
                }
            },
            remoteSort: me.remoteSort,
            sorters: me.sorters,
            remoteFilter: true,
            stickyFilters: me.stickyFilters,
            filters: me.filters,
            remoteGroup: me.remoteGroup,
            groupers: me.groupers,
            autoLoad: me.storeAutoLoad,
            autoDestroy: true
        });
        store.implicitModel = true;

        return store;
    },

    initEvents: function() {
        var me = this;

        me.callParent();

        me.view.getRowClass = me.classifyRecord;

        var sm = me.getSelectionModel();
        sm.on('select', me.onSelectRow, me);
        sm.on('deselect', me.onDeselectRow, me);
    },

    classifyRecord: function(rec, rowIndex, rowParams, store) {
        //jsl:unused rowIndex
        //jsl:unused rowParams

        return store.classifyRecord(rec);
    },

    // Stubs, eventually reimplemented by subclasses
    onSelectRow: Ext.emptyFn,
    onDeselectRow: Ext.emptyFn,

    // Reset the current selection
    onStoreLoad: function() {
        var me = this;
        var sm = me.getSelectionModel();

        me.callParent();

        // The store may not yet be bound to the selection model
        if(sm.store) {
            sm.deselectAll();
        }
    },

    // Place holder, it will be eventually replaced by the ActionPlugins
    getAllActions: function() {
        return [];
    },

    shouldDisableAction: function(act) {
        var me = this;
        var disable = me.store.shouldDisableAction(act);
        if(disable===false) {
            var cfg = act.initialConfig;
            var nsels = me.getSelectionModel().getCount();
            if(cfg.needsSelectedRow===true) {
                disable = nsels===0;
            } else if (cfg.needsOneSelectedRow===true) {
                disable = nsels!=1;
            }
        }
        return disable;
    },

    addRecord: function(index) {
        var me = this;

        var rindex;
        if(typeof index == 'number') {
            rindex = index;
        } else {
            rindex = 0;
        }

        var store = me.store;
        var newdata = me.newRecordData || {};

        if(typeof newdata == 'function') {
            newdata = newdata();
        }
        var rec = store.createNewRecord(newdata);
        if(rec) {
            store.insert(rindex, rec);
            if(me.autoShowAllEditors) {
                // Show all fields with an editor, hide all others
                var hc = me.headerCt;
                var gc = hc.getGridColumns();
                var cc = gc.length;
                for(var i=0; i<cc; i++) {
                    var c = gc[i];
                    // Ignore non-data columns (like the action column)
                    if(c.dataIndex) {
                        var f = c.field || c.editor;
                        if(f !== undefined && c.hidden===true) {
                            c.show();
                        } else if(f === undefined && c.hidden!==true) {
                            c.hide();
                        }
                    }
                }
            }
            me.getSelectionModel().select([rec]);
            return rec;
        }
        return false;
    },

    deleteRecord: function() {
        var me = this;

        var sm = me.getSelectionModel();
        var count = sm.getCount();
        var title = ngettext('Delete {0} record?', 'Delete {0} records?', count);
        var msg = ngettext('Do you really want to delete selected record?',
                           'Do you really want to delete selected records?',
                           count);
        Ext.Msg.show({
            title: Ext.String.format(title, count),
            msg: msg,
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: me,
            fn: function(response) {
                if('yes' == response) {
                    Ext.each(sm.getSelection(), function(record) {
                        record.store.deleteRecord(record);
                    });
                    sm.clearSelections();
                    if(me.immediateDeletions) {
                        me.commitChanges(null, null, true);
                    }
                }
            }
        });
    },

    commitChanges: function(callback, scope, deletions_only) {
        var me = this;
        if(me.editingPlugin) {
            me.editingPlugin.completeEdit();
        }
        me.store.commitChanges(me.saveChangesURL || me.dataURL, me.idProperty,
                               callback, scope, deletions_only);
    },

    resetChanges: function() {
        var me = this;
        if(me.editingPlugin) {
            me.editingPlugin.completeEdit();
        }
        me.store.rejectChanges();
        me.view.doStripeRows(0);
    },

    getColumnByName: function(name) {
        var me = this;
        var hc = me.headerCt;
        var gc = hc.getGridColumns();
        var cc = gc.length;
        for(var i=0; i<cc; i++) {
            var c = gc[i];
            if(c.dataIndex == name) {
                return c;
            }
        }
    }
});
