//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Store customization
// :Creato:    sab 08 set 2012 13:00:20 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/

// Fix ExtJS 4.2.1 AbstractStore load behaviour: it sends the "sorters" array
// to the server, even when "remoteSort" is false!
// Note: this seems fixed in ExtJS 5 ProxyStore (in sencha-core package).

Ext.define('MP.data.AbstractStore', {
    override: 'Ext.data.AbstractStore',

    load: function(options) {
        var me = this,
            operation;

        options = Ext.apply({
            action: 'read',
            filters: me.filters.items
        }, options);
        if (me.remoteSort) {
            options.sorters = me.getSorters();
        }
        me.lastOptions = options;

        operation = new Ext.data.Operation(options);

        if (me.fireEvent('beforeload', me, operation) !== false) {
            me.loading = true;
            me.proxy.read(operation, me.onProxyLoad, me);
        }

        return me;
    }
});

/**
 * Maintain three lists, respectively for added, updated and deleted
 * records, so that the store can give an time ordered list of changes.
 *
 * Carry also a list of sticky filters, that survives when the normal
 * filters are cleared.
 */

Ext.define("MP.data.Store", {
    extend: "Ext.data.Store",

    requires: [
        "Ext.window.MessageBox",
        "MP.window.Notification",
        "MP.data.Model"
    ],

    /**
     * @cfg {String} newRecordCls
     * Class to apply to new record
     */
    newRecordCls: 'mp-new-record',

    /**
     * @cfg {String} dirtyRecordCls
     * Class to apply to dirty (edited) record
     */
    dirtyRecordCls: 'mp-dirty-record',

    /**
     * @cfg {String} deletedRecordCls
     * Class to apply to deleted record
     */
    deletedRecordCls: 'mp-deleted-record',

    /**
     * @cfg {Object[]/Function[]} stickyFilters
     * Like the standard `filters` setting, but this collection of
     * filters is "sticky" and gets re-injected into `filters` each
     * time the latter gets cleared.
     * This is especially usefull when using the FilterBar, and you
     * need such a set of user-independent filter conditions.
     */

    constructor: function(config) {
        var me = this;

        config = Ext.merge({
            listeners: {
                add: function(store, recs /*, index*/) {
                    if(!store._add_recs) {
                        store._add_recs = [];
                    }
                    store._add_recs = store._add_recs.concat(recs);
                },

                remove: function(store, rec /*, index*/) {
                    if(!store._del_recs) {
                        store._del_recs = [];
                    }
                    if(store._del_recs.indexOf(rec) == -1) {
                        store._del_recs.push(rec);
                    }
                    Ext.Array.remove(store._add_recs, rec);
                    Ext.Array.remove(store._upd_recs, rec);
                },

                update: function(store, rec, op) {
                    if(op === Ext.data.Model.REJECT)
                        return;

                    if(store._add_recs && store._add_recs.indexOf(rec) != -1)
                        return;

                    if(store._del_recs && store._del_recs.indexOf(rec) != -1)
                        return;

                    if(!store._upd_recs) {
                        store._upd_recs = [];
                    }

                    if(store._upd_recs.indexOf(rec) == -1) {
                        store._upd_recs.push(rec);
                    }
                },

                load: function(store /*, recs, options*/) {
                    store._add_recs = [];
                    store._del_recs = [];
                    store._upd_recs = [];
                },

                clear: function(store /*, recs, options*/) {
                    store._add_recs = [];
                    store._del_recs = [];
                    store._upd_recs = [];
                }
            }
        }, config);

        var stickyFilters = me.decodeFilters(config.stickyFilters);

        delete config.stickyFilters;

        me.stickyFilters = new Ext.util.MixedCollection();
        me.stickyFilters.addAll(stickyFilters);

        me.callParent([config]);

        me.filters.addAll(me.stickyFilters.items);

        me.filters.on('clear', function() {
            me.filters.addAll(me.stickyFilters.items);
        });

        me.addEvents("reject");
    },

    /* Remove the given record from the added, updated or removed lists
     * of records, if present.
     */
    removeRecordFromLists: function(record) {
        // update added/deleted lists
        if(this._add_recs && this._add_recs.indexOf(record) != -1) {
            // if the record was just added, simply remove it from the
            // added list
            Ext.Array.remove(this._add_recs, record);
        } else if(this._del_recs && this._del_recs.indexOf(record) != -1) {
            // if the record was deleted, remove it from the deleted
            // list
            Ext.Array.remove(this._del_recs, record);
        } else if(this._upd_recs && this._upd_recs.indexOf(record) != -1) {
            // if the record was changed, remove it from the _upd_recs
            // list
            Ext.Array.remove(this._upd_recs, record);
        }
    },

    afterCommit: function(record) {
        this.removeRecordFromLists(record);
        this.callParent([record]);
    },

    afterReject: function(record) {
        var justadded = this._add_recs && this._add_recs.indexOf(record) != -1;
        this.removeRecordFromLists(record);
        if(!justadded) {
            // Don't call afterReject if the record was added (and thus
            // removed from the store), otherwise the GridView update
            // code goes into an error
            this.callParent([record]);
        } else {
            // Remove the stale (just inserted and not confirmed) record
            this.remove(record);
            if(this._del_recs) {
                Ext.Array.remove(this._del_recs, record);
            }
        }
    },

    rejectChanges: function(suppressEvent) {
        this.callParent();

        var a = this._add_recs.slice(0);
        for(var i = 0, len = a.length; i < len; i++) {
            a[i].reject();
        }

        if(this._del_recs && this._del_recs.length) {
            this._del_recs = [];
            if(!suppressEvent) {
                this.fireEvent("datachanged", this);
            }
        }

        if(this._upd_recs && this._upd_recs.length) {
            this._upd_recs = [];
            if(!suppressEvent) {
                this.fireEvent("datachanged", this);
            }
        }

        if(!suppressEvent) {
            this.fireEvent("reject", this);
        }
    },

    getRejectRecords: function() {
        var recs = [], push=Ext.Array.push;

        if(this._add_recs && this._add_recs.length) {
            push(recs, this._add_recs);
        }
        if(this._upd_recs && this._upd_recs.length) {
            push(recs, this._upd_recs);
        }
        if(this._del_recs && this._del_recs.length) {
            push(recs, this._del_recs);
        }
        return recs;
    },

    getNewRecords: function() {
        return this._add_recs || [];
    },

    getUpdatedRecords: function() {
        return this._upd_recs || [];
    },

    getDeletedRecords: function() {
        return this._del_recs || [];
    },

    isModified: function() {
        var modified = false;
        if(this.data.length>0) {
            modified = (this._upd_recs && this._upd_recs.length>0 ||
                        (this._add_recs && this._add_recs.length>0) ||
                        (this._del_recs && this._del_recs.length>0));
        }
        return modified;
    },

    /**
     * Compute the set of changes applied to the records in the store,
     * including added, updated and deleted records.
     */
    getChanges: function(changes, idfield, idfvalue, deletions_only) {
        var modified;
        var deleted;

        // <debug>
        if(!idfield) {
            Ext.Error.raise({
                msg: "getChanges(): something's wrong, idfield can't be null!",
                idfield: idfield,
                idfvalue: idfvalue
            });
        }
        // </debug>

        if(!changes) {
            modified = [];
            deleted = [];
            changes = { modified_records: modified,
                        deleted_records: deleted };
        } else {
            modified = changes.modified_records;
            if(!modified) {
                modified = [];
                changes.modified_records = modified;
            }
            deleted = changes.deleted_records;
            if(!deleted) {
                deleted = [];
                changes.deleted_records = deleted;
            }
        }

        if(this.isModified()) {
            if(!deletions_only) {
                var add_or_mod = [];
                var recs = this.getModifiedRecords();
                var len = recs.length;

                // first added or modified records
                add_or_mod = add_or_mod.concat(this._add_recs || []);
                for(var aomi=0; aomi<len; aomi++) {
                    var rec = recs[aomi];
                    if(!rec.isValid()) {
                        Ext.Msg.show({
                            title: _('Validation error'),
                            msg: _("At least one record didn't satisfy validation constraints"),
                            buttons: Ext.Msg.CANCEL,
                            icon: Ext.Msg.WARNING
                        });
                        return null;
                    }
                    if(add_or_mod.indexOf(rec)==-1) {
                        add_or_mod.push(rec);
                    }
                }

                // then other changed records
                for(var mi=0; mi<add_or_mod.length; mi++) {
                    var aom = add_or_mod[mi];
                    var cfields, idfname;

                    if(typeof idfield == 'function') {
                        idfname = idfield.call(aom);
                    } else {
                        idfname = idfield;
                    }

                    // <debug>
                    if(!idfname) {
                        Ext.Error.raise({
                            msg: "getChanges(): something's wrong, idfname can't be null!",
                            idfield: idfield
                        });
                    }
                    // </debug>

                    cfields = aom.getModifiedFields(idfname, idfvalue);

                    if(cfields) {
                        if(Ext.isObject(cfields)) {
                            modified.push([idfname, cfields]);
                        } else {
                            Ext.Msg.show({
                                title: _('Validation error'),
                                msg: Ext.String.format(
                                    _("The field “{0}” cannot be left empty"),
                                    cfields),
                                buttons: Ext.Msg.CANCEL,
                                icon: Ext.Msg.WARNING
                            });
                            return null;
                        }
                    }
                }
            }

            // finally deleted records
            var drds = this._del_recs || [];
            for(var di=0; di < drds.length; di++) {
                deleted.push([idfield, drds[di].get(idfield)]);
            }
        }

        if(modified.length>0 || deleted.length>0) {
            return changes;
        } else {
            return null;
        }
    },

    /**
     * Commit the changes, if any, with a ``POST`` Ajax request to the given url.
     */
    commitChanges: function(url, idfield, callback, scope, deletions_only) {
        var me = this;

        var changes = me.getChanges(null, idfield, null, deletions_only);
        if(!changes) {
            return;
        }

        var mrecs = changes.modified_records || [];
        var drecs = changes.deleted_records || [];

        Ext.create("MP.window.Notification", {
            position: 'br',
            title: _('Writing changes...'),
            html: _('Please wait'),
            iconCls: 'waiting-icon'
        }).show();

        var o = {
            url: url,
            method: 'POST',
            callback: function(options, success, response) {
                //jsl:unused options
                if(true !== success) {
                    var msg = response.statusText;

                    if(msg == 'Internal Server Error') {
                        msg = _('Internal server error!');
                    } else if(msg == 'communication failure') {
                        msg = _('Communication failure!');
                    }

                    Ext.create("MP.window.Notification", {
                        position: 'br',
                        title: _('Error'),
                        html: msg,
                        iconCls: 'alert-icon'
                    }).show();

                    return;
                }

                try {
                    var r = Ext.decode(response.responseText);
                } catch(e) {
                    Ext.create("MP.window.Notification", {
                        position: 'br',
                        title: _('Error'),
                        html: _('Unrecognized response'),
                        iconCls: 'alert-icon'
                    }).show();

                    me.showError(response.responseText,
                                 _('Cannot decode JSON object'));

                    return;
                }

                if(true !== r.success) {
                    Ext.create("MP.window.Notification", {
                        position: 'br',
                        title: _('Error'),
                        html: _('Write failed'),
                        iconCls: 'alert-icon'
                    }).show();

                    me.showError(r.message || _('Unknown error'));

                    return;
                }

                Ext.create("MP.window.Notification", {
                    position: 'br',
                    title: _('Done'),
                    html: _('Changes committed successfully.'),
                    iconCls: 'done-icon'
                }).show();

                me.reload();

                if(callback) {
                    callback.call(scope || me);
                }
            },
            scope: me,
            params: {
                deleted_records: Ext.encode(drecs),
                modified_records: Ext.encode(mrecs)
            }
        };
        Ext.Ajax.request(o);
    },

    showError:function(msg, title) {
        Ext.Msg.show({
            title: title || _('Error'),
            msg: Ext.util.Format.ellipsis(msg, 2000),
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
            minWidth: 1200 > String(msg).length ? 360 : 600
        });
    },

    /**
     * Determine the CSS class to apply to the given record, accordingly to
     * its current state within this store.
     */
    classifyRecord: function(rec) {
        if(this._del_recs && this._del_recs.indexOf(rec) != -1) {
            return this.deletedRecordCls;
        } else if (this._add_recs && this._add_recs.indexOf(rec) != -1) {
            return this.newRecordCls;
        } else if (this._upd_recs && this._upd_recs.indexOf(rec) != -1) {
            return this.dirtyRecordCls;
        }
        return '';
    },

    deleteRecord: function(rec) {
        if(!this._del_recs) {
            this._del_recs = [];
        }
        if(this._add_recs.indexOf(rec) != -1) {
            // It's a new record, remove it immediately
            this.remove(rec);
            Ext.Array.remove(this._del_recs, rec);
            this.fireEvent("datachanged", this);
        } else if(this._del_recs.indexOf(rec) == -1) {
            this._del_recs.push(rec);
            if (this._upd_recs) {
                Ext.Array.remove(this._upd_recs, rec);
            }
            this.fireEvent("update", this, rec, Ext.data.Record.EDIT, []);
            this.fireEvent("datachanged", this);
        }
    },

    createNewRecord: function(initialdata) {
        var me = this;

        if(me.model) {
            var data = {};
            var fnames = me.model.prototype.fields.keys;

            if(initialdata) {
                Ext.apply(data, initialdata);
            }

            // Set missing fields to null
            for(var fi=0,fl=fnames.length; fi<fl; fi++) {
                var name = fnames[fi];
                if(typeof data[name] == 'undefined') {
                    data[name] = null;
                }
            }

            var record = new me.model(data);

            // Do consider initial data as changes
            if(initialdata) {
                var modified = record.modified;

                for(var fname in initialdata) {
                    modified[fname] = undefined;
                }
            }

            return record;
        } else {
            return false;
        }
    },

    /**
     * Gets the total number of records in the dataset as returned
     * by the server, plus eventual additions.
     */
    getTotalCount : function() {
        return (this.totalCount || 0) + (this._add_recs ? this._add_recs.length : 0);
    },

    /**
     * Determine whether the given action should be disabled, accordingly
     * to its configuration and current store state.
     */
    shouldDisableAction: function(act) {
        if(!act.setDisabled) { return null; }
        var cfg = act.initialConfig;
        if(this.isModified()) {
            if(cfg.needsDirtyState===false || cfg.needsCleanStore===true) {
                return true;
            }
        } else {
            if(cfg.needsDirtyState===true || cfg.needsCleanStore===false) {
                return true;
            }
        }
        return false;
    },

    /**
     * Like filter(), but treat the given filters collection as
     * sticky. The noImmediateReload argument, if true, skips the
     * immediate reload of the store.
     */
    stickyFilter: function(filters, value, noImmediateReload) {
        if (Ext.isString(filters)) {
            filters = {
                property: filters,
                value: value
            };
        } else {
            noImmediateReload = value;
        }

        var me = this,
            decoded = me.decodeFilters(filters),
            i = 0, length = decoded.length;

        for (; i < length; i++) {
            me.stickyFilters.replace(decoded[i]);
        }

        if(noImmediateReload) {
            me.filters.addAll(me.stickyFilters.items);
        } else {
            me.filter(decoded);
        }
    },

    /**
     * Reset the sticky filters collection, adjusting the standard
     * filters too. Finally reload the store.
     */
    clearStickyFilter: function(suppressEvent) {
        var me = this;
        var slen = me.stickyFilters.length;
        var sitems = me.stickyFilters.items;

        // Remove corresponding items from the standard filters

        for (var s = 0; s < slen; s++) {
            var si = sitems[s];
            var flen = me.filters.length;
            var fitems = me.filters.items;

            for (var f = 0; f < flen; f++) {
                var fi = fitems[f];

                if (fi.property == si.property && fi.value == si.value) {
                    me.filters.removeAt(f);
                    break;
                }
            }
        }

        me.stickyFilters.clear();

        // Eventually refresh the store; too bad we need to copy here
        // this piece of code from the standard store :-\

        if (me.remoteFilter) {

            // In a buffered Store, the meaning of suppressEvent is to
            // simply clear the filters collection
            if (suppressEvent) {
                return;
            }

            // So that prefetchPage does not consider the store to be
            // fully loaded if the local count is equal to the total
            // count
            delete me.totalCount;

            // For a buffered Store, we have to clear the prefetch
            // cache because the dataset will change upon filtering.
            // Then we must prefetch the new page 1, and when that
            // arrives, reload the visible part of the Store via the
            // guaranteedrange event
            if (me.buffered) {
                me.pageMap.clear();
                me.loadPage(1);
            } else {
                // Reset to the first page, clearing a filter will
                // destroy the context of the current dataset
                me.currentPage = 1;
                me.load();
            }
        } else if (me.isFiltered()) {
            me.data = me.snapshot.clone();
            delete me.snapshot;

            if (suppressEvent !== true) {
                me.fireEvent('datachanged', me);
                me.fireEvent('refresh', me);
            }
        }
    }
});
