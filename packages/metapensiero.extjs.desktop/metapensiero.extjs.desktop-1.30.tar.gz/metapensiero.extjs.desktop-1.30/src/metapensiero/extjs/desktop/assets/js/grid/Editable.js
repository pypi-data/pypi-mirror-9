//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Editable grid
// :Creato:    mer 05 dic 2012 15:35:03 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/


// Seems to fix many issues with columns in 4.2.1 grids
// since we now cache all columns instead of just visible ones...
// See http://www.sencha.com/forum/showthread.php?264959-4.2.1.833-Exception-when-editing-a-cell-of-previously-hidden-column

Ext.define('MP.grid.ColumnManager', {
    override: 'Ext.grid.ColumnManager',

    cacheColumns: function()
    {
        this.columns = this.headerCt.getGridColumns();
        if (this.secondHeaderCt)
        {
            Ext.Array.push(this.columns, this.secondHeaderCt.getGridColumns());
        }
    }
});


// Fix the walkCells() method of Ext.view.Table, that when there are hidden columns at the
// right end of the grid, it fails to properly wrap to the next row.

Ext.define('MP.view.Table', {
    override: 'Ext.view.Table',

    walkCells: function(pos, direction, e, preventWrap, verifierFn, scope) {

        // Caller (probably CellModel) had no current position. This can happen
        // if the main el is focused and any navigation key is presssed.
        if (!pos) {
            return false;
        }

        var me           = this,
            row          = pos.row,
            column       = pos.column,
            rowCount     = me.dataSource.getCount(),
            cmgr         = me.ownerCt.columnManager,
            lastCol      = cmgr.getColumns().length - 1,
            newRow       = row,
            newColumn    = column,
            activeHeader = cmgr.getHeaderAtIndex(column);

        // no active header or its currently hidden
        if (!activeHeader || activeHeader.hidden || !rowCount) {
            return false;
        }

        // This is the fix: skip hidden columns at the end, otherwise the check
        // "column === lastCol" below won't ever happen and thus the cursor will
        // never wrap to the next row
        for (var lch = cmgr.getHeaderAtIndex(lastCol);
             lastCol && lch && lch.hidden;
             lch = cmgr.getHeaderAtIndex(--lastCol))
            /* do nothing */;

        e = e || {};
        direction = direction.toLowerCase();
        switch (direction) {
            case 'right':
                // has the potential to wrap if its last
                if (column === lastCol) {
                    // if bottom row and last column, deny right
                    if (preventWrap || row === rowCount - 1) {
                        return false;
                    }
                    if (!e.ctrlKey) {
                        // otherwise wrap to nextRow and firstCol
                        newRow = me.walkRows(row, 1);
                        if (newRow !== row) {
                            newColumn = 0;
                        }
                    }
                    // go right
                } else {
                    if (!e.ctrlKey) {
                        newColumn = column + 1;
                    } else {
                        newColumn = lastCol;
                    }
                }
                break;

            case 'left':
                // has the potential to wrap
                if (column === 0) {
                    // if top row and first column, deny left
                    if (preventWrap || row === 0) {
                        return false;
                    }
                    if (!e.ctrlKey) {
                        // otherwise wrap to prevRow and lastCol
                        newRow = me.walkRows(row, -1);
                        if (newRow !== row) {
                            newColumn = lastCol;
                        }
                    }
                    // go left
                } else {
                    if (!e.ctrlKey) {
                        newColumn = column - 1;
                    } else {
                        newColumn = 0;
                    }
                }
                break;

            case 'up':
                // if top row, deny up
                if (row === 0) {
                    return false;
                    // go up
                } else {
                    if (!e.ctrlKey) {
                        newRow = me.walkRows(row, -1);
                    } else {
                        // Go to first row by walking down from row -1
                        newRow = me.walkRows(-1, 1);
                    }
                }
                break;

            case 'down':
                // if bottom row, deny down
                if (row === rowCount - 1) {
                    return false;
                    // go down
                } else {
                    if (!e.ctrlKey) {
                        newRow = me.walkRows(row, 1);
                    } else {
                        // Go to first row by walking up from beyond the last row
                        newRow = me.walkRows(rowCount, -1);
                    }
                }
                break;
        }

        if (verifierFn && verifierFn.call(scope || me, {row: newRow, column: newColumn}) !== true) {
            return false;
        } else {
            return new Ext.grid.CellContext(me).setPosition(newRow, newColumn);
        }
    }
});


Ext.define('MP.grid.Editable', {
    extend: 'MP.grid.Basic',

    requires: [
        'Ext.grid.plugin.CellEditing',
        'MP.action.AddAndDelete'
    ],

    /**
     * @cfg {Bool} noAddAndDelete
     * Set it to true to disable the automatic creation of the “add”
     * and “delete” actions
     */
    noAddAndDelete: false,

    initComponent: function() {
        var me = this;

        if(!me.readOnly) {
            Ext.each(me.columns, function(c) {
                if(c.editor && c.editor.lookupFor) {
                    var fname = c.editor.lookupFor;
                    var iname = c.editor.store.proxy.reader.idProperty;
                    var listeners = {
                        change: function(combo) {
                            if(combo.getRawValue()==='') {
                                var record = me.getSelectionModel().getSelection()[0];
                                record.set(fname, null);
                            }
                        },
                        select: function(combo, selected) {
                            //jsl:unused combo
                            var record = me.getSelectionModel().getSelection()[0];
                            record.set(fname, selected[0].get(iname));
                        }
                    };
                    if(c.editor.isComponent) {
                        c.editor.on(listeners);
                    } else {
                        if(c.editor.listeners) {
                            Ext.apply(c.editor.listeners, listeners);
                        } else {
                            c.editor.listeners = listeners;
                        }
                    }
                }
            });

            var cellEditing = null;

            if(me.clicksToEdit) {
                cellEditing = Ext.create('Ext.grid.plugin.CellEditing', {
                    clicksToEdit: me.clicksToEdit
                });
            }

            if(!me.plugins) {
                me.plugins = [];
            }

            if(cellEditing) {
                me.plugins.push(cellEditing);

                // End cell editing when switching to another tab
                // panel
                me.on('hide', function() {
                    me.editingPlugin.completeEdit();
                });
            }

            if(!me.noAddAndDelete) {
                me.plugins.push(Ext.create('MP.action.AddAndDelete'));
            }
        }

        me.callParent();
    },

    initEvents: function() {
        var me = this;

        me.callParent();

        if(!me.readOnly) {
            me.on("itemcontextmenu", function(view, record, item, index, e) {
                var items = [];
                var addndel = MP.action.AddAndDelete;

                Ext.each(me.getAllActions(), function(act) {
                    if(act.itemId != addndel.ADD_ACTION
                       && act.itemId != addndel.DELETE_ACTION
                       && act.initialConfig
                       && act.initialConfig.handler
                       && act.initialConfig.needsOneSelectedRow
                       && !act.isDisabled()) {
                        items.push({
                            text: act.initialConfig.text,
                            tooltip: act.initialConfig.tooltip,
                            iconCls: act.initialConfig.iconCls,
                            handler: act.execute.bind(act)
                        });
                    }
                });
                e.stopEvent();
                if(items.length>0) {
                    var pm = new Ext.menu.Menu({
                        items: items
                    });
                    var coords = e.getXY();
                    pm.showAt([coords[0], coords[1]]);
                }
            });
        }
    }
});
