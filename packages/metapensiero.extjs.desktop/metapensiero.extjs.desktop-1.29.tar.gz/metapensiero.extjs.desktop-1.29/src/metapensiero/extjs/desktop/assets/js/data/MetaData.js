//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- MetaData manager
// :Creato:    dom 18 nov 2012 21:21:28 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare _*/


Ext.define('MP.data.MetaData', {
    requires: [
        'Ext.Ajax',
        'Ext.window.MessageBox',
        'Ext.util.Format'
    ],

    uses: [
        'Ext.form.field.*',
        'Ext.grid.column.Boolean',
        'Ext.grid.column.Date',
        'Ext.grid.column.Number',
        'Ext.data.Store',
        'Ext.data.proxy.Ajax',
        'Ext.data.reader.Json',
        'Ext.util.MixedCollection'
    ],

    statics: {
        cache: {},

        /**
         * Fetch the metadata configuration from the given URL, executing
         * the callback with an instance of this class as the only
         * parameter if everything goes well, otherwise call the
         * error_callback with the result of the AJAX request.
         * Instances are kept in a cache, keyed on the associated URL,
         * so subsequent calls with the same URL will reuse the same
         * instance, without fetching the configuration again.
         */
        fetch: function(url, scope, callback, error_callback) {
            var me = this;
            var cache = me.cache;
            var md = cache[url];

            if(md) {
                callback.call(scope, md);
            } else {
                this.request(
                    url, { metadata: 'metadata', limit: 0 },
                    function(metadata) {
                        md = new MP.data.MetaData(metadata);
                        cache[url] = md;
                        callback.call(scope, md);
                    }, error_callback);
            }
        },

        /**
         * Clear the instances cache.
         */
        clearCache: function() {
            var cache = this.cache;

            for(var url in cache) {
                if(cache.hasOwnProperty(url)) {
                    delete cache[url];
                }
            }
        },

        /**
         * Perform an AJAX GET of the given URL, which should return a
         * JSON encoded dictionary with a `success` flag, a `message`
         * string and a `metadata` dictionary with the configuration.
         * If everything goes well, execute the callback passing the
         * decoded `metadata`. Otherwise execute the error_callback,
         * if given, passing the result of the AJAX request.
         */
        request: function(url, params, callback, error_callback) {
            Ext.Ajax.request({
                url: url,
                params: params,
                method: 'GET',
                disableCaching: true,
                scope: this,

                success: function (r) {
                    var res = Ext.decode(r.responseText);
                    if(!res) {
                        Ext.MessageBox.alert(
                            _("Couldn't fetch configuration"),
                            _('Cannot decode JSON object obtained from ')+url);
                        if(error_callback) error_callback(r);
                    } else {
                        if(res.success && Ext.isObject(res.metadata)) {
                            callback(res.metadata);
                        } else {
                            Ext.MessageBox.alert(
                                _("Couldn't fetch configuration"),
                                _('Invalid response from ')+url);
                            if(error_callback) error_callback(r);
                        }
                    }
                },

                failure: function (r) {
                    if(r.status >= 400) {
                        Ext.MessageBox.alert(r.statusText, r.responseText);
                    } else {
                        var res = r.responseText && Ext.decode(r.responseText);
                        if(res) {
                            Ext.MessageBox.alert(
                                // TRANSLATORS: {0} is the error code, {1} the error message
                                Ext.String.format(_('Communication error ({0} {1})'),
                                                  r.status, r.statusText),
                                res.message);
                        } else {
                            Ext.MessageBox.alert(_('Communication error'),
                                                 r.statusText);
                        }
                    }
                    if(error_callback) error_callback(r);
                }
            });
        },

        renderBoolean: function(value) {
            return (value===true) ? _('Yes') : _('No');
        },

        renderDate: function(value) {
            // TRANSLATORS: this is the format used to display dates, see
            // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date for details
            // on the syntax.
            return Ext.util.Format.date(value, _('m/d/Y'));
        },

        renderTime: function(value) {
            // TRANSLATORS: this is the format used to display time of the day, see
            // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date for details
            // on the syntax.
            return Ext.util.Format.date(value, _('g:i A'));
        },

        renderTimestamp: function(value) {
            // TRANSLATORS: this is the format used to display timestamps, see
            // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date for details
            // on the syntax.
            return Ext.util.Format.date(value, _('m/d/Y g:i:s A'));
        }
    },

    // Regexp used to recognize fields coming from the DB, to be
    // saved back. Computed fields should be CamelCased.
    validFieldName: /^[a-z][a-z0-9_]+$/,

    /**
     * Create an instance of this class, storing the configuration
     * from the given `metadata`.
     */
    constructor: function(metadata) {
        var me = this;

        me.primary_key = metadata.primary_key;
        me.count_slot = metadata.count_slot;
        me.root_slot = metadata.root_slot;
        me.success_slot = metadata.success_slot;
        me.fields_info = new Ext.util.MixedCollection(
            false, function(info) {return info.name; });
        me.fields_info.addAll(metadata.fields);
    },

    /**
     * Extract an array of Ext.data.Field descriptions usable to
     * configure a Ext.data.Store. The optional `overrides` argument
     * may be a dictionary, keyed on the field name, of dictionaries,
     * used to overwrite settings provided by the server.
     */
    fields: function(overrides) {
        var me = this;
        var fields = [];

        me.fields_info.each(function(info) {
            var override = {};
            if(overrides) {
                Ext.apply(override, overrides[info.name], overrides['*']);
            }
            var sendback = (info.sendback === true
                            || info.name.match(me.validFieldName)) && (
                                override.sendback !== false);
            var field = { name: info.name,
                          type: info.type,
                          useNull: info.nullable || override.nullable,
                          allowBlank: info.nullable || override.nullable,
                          sendBackToServer: sendback
                        };

            if(info.type==='date') {
                field.dateFormat = info.format;
            }

            fields.push(field);
        });

        return fields;
    },

    /**
     * Extract an array of Ext.grid.Column descriptions usable to
     * configure a Ext.grid.Panel. The optional `overrides` argument
     * may be a dictionary, keyed on the field name, of dictionaries,
     * used to overwrite settings provided by the server. Under the
     * key “*” may be passed an overriding dictionary applied to all
     * columns. Both the field specific entry and the global entry
     * (“*”) may be a function, and in that case it will be called
     * with the whole field info as argument and should return the
     * computed settings.
     *
     * If `editable` is given and has a false value, columns will be
     * readonly and no editor will be attached.
     */
    columns: function(overrides, editable) {
        var me = this;
        var editors = null;
        var columns = [];

        if(editable === undefined) {
            editable = true;
        }

        if(editable) {
            editors = me.editors(Ext.apply({}, overrides,
                                           {'*': {fieldLabel: null}}));
        }

        me.fields_info.each(function(info) {
            var readonly;
            var override = { hidden: info.hidden };
            var column = { text: info.label,
                           tooltip: info.hint,
                           dataIndex: info.name,
                           sortable: true,
                           flex: info.flex
                         };

            if(overrides) {
                var cfg = overrides[info.name];
                var dfl = overrides['*'];

                if(dfl) {
                    if(Ext.isFunction(dfl)) {
                        dfl = dfl.call(this, info);
                    }
                    Ext.apply(override, dfl);
                    delete override.editor;
                }

                if(cfg) {
                    if(Ext.isFunction(cfg)) {
                        cfg = cfg.call(this, info);
                    }
                    Ext.apply(override, cfg);
                    delete override.editor;
                }
            }

            if(editable) {
                if(override.readonly !== undefined) {
                    readonly = override.readonly;
                } else {
                    readonly = info.readonly;
                }
            } else {
                readonly = true;
            }

            if(info.dictionary) {
                var dict;

                if(Ext.isArray(info.dictionary)) {
                    dict = {};
                    Ext.each(info.dictionary, function(v) {
                        dict[v[0]] = v[1];
                    });
                } else {
                    dict = info.dictionary;
                }

                // Use a closure to keep a reference to the dict
                column.renderer = Ext.bind(function(value) {
                    return this[value];
                }, dict);

                // TODO: factorize the following code with the equivalent in the
                //       editors() method

                var store;

                if(Ext.isArray(info.dictionary)) {
                    // Make a copy, so caller may safely alter it
                    store = [].concat(info.dictionary);
                } else {
                    var sortby = 0; // key by default
                    var d = info.dictionary;
                    store = [];

                    for(var k in d) {
                        if(k == '__sort_by__') {
                            sortby = (d[k] == 'value' ? 1 : 0);
                        } else {
                            store.push([k, d[k]]);
                        }
                    }

                    store.sort(function(a,b) {
                        a = a[sortby];
                        b = b[sortby];
                        return a<b ? -1 : (a>b ? 1 : 0);
                    });
                }

                column.filter = {
                    xtype: 'combo',
                    store: store,
                    triggerAction: 'all',
                    typeAhead: true,
                    forceSelection: true,
                    allowBlank: true,
                    minChars: 0
                };
            } else if(info.lookup && info.lookup.url) {
                // TODO: factorize the following code with the equivalent in the
                //       editors() method

                var lup = info.lookup;
                var idField = lup.idField || 'id';
                var flds = [idField];
                var displayField = lup.displayField;
                var otherFields = lup.otherFields;

                if(displayField) {
                    flds.push(displayField);
                }
                if(otherFields) {
                    if(!Ext.isArray(otherFields)) {
                        otherFields = otherFields.split(',');
                    }
                    flds = flds.concat(otherFields);
                }

                var model = Ext.define('MP.data.ImplicitModel-'+Ext.id(), {
                    extend: 'Ext.data.Model',
                    fields: flds,
                    idProperty: idField
                });

                var remoteFilter = lup.remoteFilter===undefined ? true : lup.remoteFilter;
                var remoteSort = lup.remoteSort===undefined ? true : lup.remoteSort;

                var lstore = Ext.create('Ext.data.Store', {
                    model: model,
                    pageSize: lup.pageSize === undefined ? 999 : lup.pageSize,
                    autoLoad: !remoteFilter || !remoteSort,
                    remoteFilter: remoteFilter,
                    remoteSort: remoteSort,
                    sorters: lup.sorters,
                    proxy: {
                        type: 'ajax',
                        url: lup.url,
                        filterParam: 'filters',
                        reader: {
                            type: 'json',
                            root: lup.resultSlot || 'root',
                            idProperty: idField,
                            totalProperty: lup.countSlot || 'count'
                        }
                    }
                });
                lstore.implicitModel = true;

                var listConfig = {};

                if(lup.innerTpl) {
                    listConfig.getInnerTpl = Ext.bind(function() {
                        return this.innerTpl;
                    }, lup);
                }

                if(lup.pageSize !== undefined) {
                    listConfig.createPagingToolbar = function() {
                        return Ext.widget('pagingtoolbar', {
                            id: this.id + '-paging-toolbar',
                            pageSize: this.pageSize,
                            store: this.dataSource,
                            border: false,
                            ownerCt: this,
                            ownerLayout: this.getComponentLayout(),
                            getPagingItems: function() {
                                var items;

                                items = Ext.toolbar.Paging.prototype.getPagingItems.call(this);

                                // Keep only the buttons
                                items = Ext.Array.filter(items, function(i) {
                                    return i.itemId == 'first' ||
                                        i.itemId == 'prev' ||
                                        i.itemId == 'next' ||
                                        i.itemId == 'last';
                                });

                                // Force horizontal centering
                                items.unshift('->');
                                items.push('->');

                                return items;
                            }
                        });
                    };
                }

                column.filter = {
                    xtype: 'combo',
                    store: lstore,
                    displayField: displayField || idField,
                    loadingText: _('Loading...'),
                    triggerAction: 'all',
                    typeAhead: true,
                    forceSelection: true,
                    allowBlank: true,
                    minChars: 0,
                    pageSize: lup.pageSize,
                    listConfig: listConfig
                };
            } else if(info.type === 'string') {
                var password = info.password === true;

                if(password) {
                    column.renderer = function() { return '*****'; };
                    column.filter = false;
                } else {
                    column.filter = true;
                }
            } else if(info.type === 'boolean') {
                if(readonly) {
                    column.xtype = 'booleancolumn';
                } else {
                    column.xtype = 'checkcolumn';
                }
                column.filter = true;
            } else if(info.type === 'date') {
                column.xtype = 'datecolumn';
                column.renderer = (info.timestamp
                                   ? MP.data.MetaData.renderTimestamp
                                   : (info.time
                                      ? MP.data.MetaData.renderTime
                                      : MP.data.MetaData.renderDate));
                column.filter = { type: 'date' };
            } else {
                if(info.decimals) {
                    var decimals = info.decimals;
                    column.renderer = function (v) {
                        if(v!='' && v!=null) {
                            return v.toFixed(decimals);
                        } else {
                            return v;
                        }
                    };
                    column.filter = { type: 'float' };
                } else {
                    column.filter = { type: 'int' };
                }
            }

            if(info.align !== undefined) {
                column.align = info.align;
            }
            if(info.width !== undefined) {
                column.width = info.width;
            }
            if(info.sortable !== undefined) {
                column.sortable = info.sortable;
            }

            if(!readonly && editors && info.name in editors) {
                column.editor = editors[info.name];
                column.editor.fieldLabel = null;
            }

            Ext.apply(column, override);

            columns.push(column);
        });

        return columns;
    },

    /**
     * Extract a dictionary of Ext.form.Field configurations, one for
     * each non readonly field. The optional `overrides` argument may
     * be a dictionary, keyed on the field name, of dictionaries of
     * which the `editor` slot is used to overwrite settings provided
     * by the server. Under the key “*” may be passed an overriding
     * dictionary applied to all editors. Both the field specific
     * entry and the global entry (“*”) may be a function, and in that
     * case it will be called with the whole field info as argument
     * and should return the computed settings.
     */
    editors: function(overrides) {
        var me = this;
        var editors = {};

        me.fields_info.each(function(info) {
            var readonly;
            var override = {};
            var editor = {
                fieldLabel: info.label,
                name: info.name
            };

            if(overrides) {
                var cfg = overrides[info.name];
                var dfl = overrides['*'];

                if(dfl && dfl.editor) {
                    dfl = dfl.editor;
                    if(Ext.isFunction(dfl)) {
                        dfl = dfl.call(this, info);
                    }
                    Ext.apply(override, dfl);
                }

                if(cfg && cfg.editor) {
                    cfg = cfg.editor;
                    if(Ext.isFunction(cfg)) {
                        cfg = cfg.call(this, info);
                    }
                    Ext.apply(override, cfg);
                }
            }

            if(override.readonly !== undefined) {
                readonly = override.readonly;
            } else {
                readonly = info.readonly;
            }

            if(readonly)
                return;

            var nullable = info.nullable;
            if(override.nullable !== undefined) {
                nullable = override.nullable;
                delete override['nullable'];
            }

            if(info.dictionary) {
                var store;

                if(Ext.isArray(info.dictionary)) {
                    // Make a copy, so caller may safely alter it
                    store = [].concat(info.dictionary);
                } else {
                    var sortby = 0; // key by default
                    var dict = info.dictionary;

                    store = [];

                    for(var k in dict) {
                        if(k == '__sort_by__') {
                            sortby = (dict[k] == 'value' ? 1 : 0);
                        } else {
                            store.push([k, dict[k]]);
                        }
                    }

                    store.sort(function(a,b) {
                        a = a[sortby];
                        b = b[sortby];
                        return a<b ? -1 : (a>b ? 1 : 0);
                    });
                }

                Ext.apply(editor, {
                    xtype: 'combo',
                    store: store,
                    triggerAction: 'all',
                    typeAhead: true,
                    allowBlank: nullable
                });
            } else if(info.lookup) {
                var lup = info.lookup;

                if(lup.url) {
                    var idField = lup.idField || 'id';
                    var flds = [idField];
                    var displayField = lup.displayField;
                    var otherFields = lup.otherFields;

                    if(displayField) {
                        flds.push(displayField);
                    }
                    if(otherFields) {
                        if(!Ext.isArray(otherFields)) {
                            otherFields = otherFields.split(',');
                        }
                        flds = flds.concat(otherFields);
                    }

                    var model = Ext.define('MP.data.ImplicitModel-'+Ext.id(), {
                        extend: 'Ext.data.Model',
                        fields: flds,
                        idProperty: idField
                    });

                    var remoteFilter = lup.remoteFilter===undefined ? true : lup.remoteFilter;
                    var remoteSort = lup.remoteSort===undefined ? true : lup.remoteSort;

                    var lstore = Ext.create('Ext.data.Store', {
                        model: model,
                        pageSize: lup.pageSize === undefined ? 999 : lup.pageSize,
                        autoLoad: !remoteFilter || !remoteSort,
                        remoteFilter: remoteFilter,
                        remoteSort: remoteSort,
                        sorters: lup.sorters,
                        proxy: {
                            type: 'ajax',
                            url: lup.url,
                            filterParam: 'filters',
                            reader: {
                                type: 'json',
                                root: lup.resultSlot || 'root',
                                idProperty: idField,
                                totalProperty: lup.countSlot || 'count'
                            }
                        }
                    });
                    lstore.implicitModel = true;

                    var listConfig = {};

                    if(lup.innerTpl) {
                        listConfig.getInnerTpl = Ext.bind(function() {
                            return this.innerTpl;
                        }, lup);
                    }

                    if(lup.pageSize !== undefined) {
                        listConfig.createPagingToolbar = function() {
                            return Ext.widget('pagingtoolbar', {
                                id: this.id + '-paging-toolbar',
                                pageSize: this.pageSize,
                                store: this.dataSource,
                                border: false,
                                ownerCt: this,
                                ownerLayout: this.getComponentLayout(),
                                getPagingItems: function() {
                                    var items;

                                    items = Ext.toolbar.Paging.prototype.getPagingItems.call(this);

                                    // Keep only the buttons
                                    items = Ext.Array.filter(items, function(i) {
                                        return i.itemId == 'first' ||
                                            i.itemId == 'prev' ||
                                            i.itemId == 'next' ||
                                            i.itemId == 'last';
                                    });

                                    // Force horizontal centering
                                    items.unshift('->');
                                    items.push('->');

                                    return items;
                                }
                            });
                        };
                    }

                    Ext.apply(editor, {
                        xtype: 'combo',
                        store: lstore,
                        lookupFor: lup.lookupField || idField,
                        displayField: displayField || idField,
                        loadingText: _('Loading...'),
                        triggerAction: 'all',
                        typeAhead: true,
                        selectOnFocus: true,
                        allowBlank: nullable,
                        minChars: 3,
                        pageSize: lup.pageSize,
                        listConfig: listConfig
                    });
                } else {
                    Ext.apply(editor, {
                        xtype: 'triggerfield',
                        triggerClass: 'x-form-search-trigger'
                    });
                }
            } else if(info.type === 'string') {
                if(info.length) {
                    Ext.apply(editor, {
                        xtype: 'textfield',
                        allowBlank: nullable,
                        inputType: info.password === true ? 'password' : 'text',
                        selectOnFocus: info.password === true,
                        vtype: info.vtype,
                        vtypeText: info.vtypeText,
                        maxLength: info.length,
                        enforceMaxLength: true,
                        regex: info.regexp ? new RegExp(info.regexp) : undefined
                    });
                } else {
                    Ext.apply(editor, {
                        xtype: 'textareafield',
                        allowBlank: nullable
                    });
                }
                if(info.uppercase) {
                    //editor.style = {textTransform: "uppercase"};
                    editor.listeners = {
                        change: function(field, newValue) {
                            field.setValue(newValue.toUpperCase());
                        }
                    };
                }
            } else if(info.type === 'boolean') {
                Ext.apply(editor, {
                    xtype: 'checkbox',
                    cls: 'x-grid-checkheader-editor'
                });
            } else if(info.type === 'date') {
                if(info.time) {
                    Ext.apply(editor, {
                        xtype: 'timefield',
                        allowBlank: nullable,
                        format: _('g:i A')
                    });
                } else {
                    Ext.apply(editor, {
                        xtype: 'datefield',
                        allowBlank: nullable,
                        format: (info.timestamp
                                 ? _('m/d/Y g:i:s A')
                                 : _('m/d/Y'))
                    });
                }
            } else {
                Ext.apply(editor, {
                    xtype: 'numberfield',
                    selectOnFocus: true,
                    allowBlank: nullable
                });
                if(info.decimals !== undefined) {
                    editor.allowDecimals = info.decimals != 0;
                    editor.decimalPrecision = info.decimals;
                }
            }

            if(typeof info.width != 'undefined') {
                editor.width = info.width;
            }
            if(typeof info.height != 'undefined') {
                editor.height = info.height;
            }
            if(typeof info.anchor != 'undefined') {
                editor.anchor = info.anchor;
            }
            if(typeof info.min != 'undefined') {
                editor.minValue = info.min;
            }
            if(typeof info.max != 'undefined') {
                editor.maxValue = info.max;
            }

            Ext.apply(editor, override);

            editors[info.name] = editor;
        });

        return editors;
    }
});
