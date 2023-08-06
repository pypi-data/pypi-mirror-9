/*jsl:declare Ext*/
/*jsl:declare _*/

/**
 * The grid displaying the list of uploaded files (queue).
 *
 * @class MP.upload.ItemGridPanel
 * @extends Ext.grid.Panel
 */
Ext.define('MP.upload.ItemGridPanel', {
    extend : 'Ext.grid.Panel',

    requires : [
        'Ext.selection.CheckboxModel',
        'MP.upload.Store'
    ],

    layout : 'fit',
    border : 0,

    viewConfig : {
        scrollOffset : 40
    },

    config : {
        queue : null,

        textFilename : _('Filename'),
        textSize : _('Size'),
        textType : _('Content type'),
        textStatus : _('Status'),
        textProgress : '%'
    },

    constructor : function(config) {
        this.initConfig(config);

        return this.callParent(arguments);
    },

    initComponent : function() {
        var columns = this.getGridColumnsConfig();

        if (this.queue) {
            this.queue.on('queuechange', this.onQueueChange, this);
            this.queue.on('itemchangestatus', this.onQueueItemChangeStatus, this);
            this.queue.on('itemprogressupdate', this.onQueueItemProgressUpdate, this);
        }

        if (!this.store) {
            this.store = Ext.create('MP.upload.Store');
        }

        Ext.apply(this, {
            selModel : Ext.create('Ext.selection.CheckboxModel', {
                checkOnly : true
            }),
            columns : columns
        });

        this.callParent(arguments);
    },

    getGridColumnsConfig : function() {
        return [
            {
                xtype : 'rownumberer',
                width : 25
            }, {
                id : 'filename',
                dataIndex : 'filename',
                header : this.textFilename,
                flex : 1
            }, {
                dataIndex : 'size',
                header : this.textSize,
                width : 100,
                renderer : function(value) {
                    return Ext.util.Format.fileSize(value);
                }
            }, {
                dataIndex : 'contenttype',
                header : this.textType,
                width : 130
            }, {
                dataIndex : 'status',
                header : this.textStatus,
                width : 50,
                align : 'right',
                renderer : this.statusRenderer
            }, {
                dataIndex : 'progress',
                header : this.textProgress,
                width : 50,
                align : 'right',
                renderer : function(value) {
                    if (!value) {
                        value = 0;
                    }
                    return value + '%';
                }
            }
        ];
    },

    onQueueChange : function(queue) {
        this.loadQueueItems(queue.getItems());
    },

    onQueueItemChangeStatus : function(queue, item) {
        //jsl:unused queue
        this.updateStatus(item);
    },

    onQueueItemProgressUpdate : function(queue, item) {
        //jsl:unused queue
        this.updateStatus(item);
    },

    /**
     * Loads the internal store with the supplied queue items.
     *
     * @param {Array} items
     */
    loadQueueItems : function(items) {
        var data = [];
        var i;

        for (i = 0; i < items.length; i++) {
            data.push([
                items[i].getFilename(),
                items[i].getSize(),
                items[i].getContentType(),
                items[i].getStatus(),
                items[i].getProgressPercent()
            ]);
        }

        this.loadStoreData(data);
    },

    loadStoreData : function(data, append) {
        this.store.loadData(data, append);
    },

    getSelectedRecords : function() {
        return this.getSelectionModel().getSelection();
    },

    updateStatus : function(item) {
        var record = this.getRecordByFilename(item.getFilename());
        if (!record) {
            return;
        }

        var itemStatus = item.getStatus();

        if (itemStatus != record.get('status')) {
            this.scrollIntoView(record);

            record.set('status', item.getStatus());
            if (item.isUploadError()) {
                record.set('tooltip', item.getUploadErrorMessage());
            }
        }

        record.set('progress', item.getProgressPercent());
        record.commit();
    },

    getRecordByFilename : function(filename) {
        var index = this.store.findExact('filename', filename);
        if (-1 == index) {
            return null;
        }

        return this.store.getAt(index);
    },

    getIndexByRecord : function(record) {
        return this.store.findExact('filename', record.get('filename'));
    },

    statusRenderer : function(value, metaData, record, rowIndex, colIndex, store) {
        //jsl:unused metaData
        //jsl:unused rowIndex
        //jsl:unused colIndex
        //jsl:unused store
        var iconCls = 'mp-upload-icon-upload-' + value;
        var tooltip = record.get('tooltip');
        if (tooltip) {
            value = tooltip;
        } else {
            value = _(value);
        }
        value = '<span class="mp-upload-status-value ' + iconCls + '" data-qtip="' + value + '" />';
        return value;
    },

    scrollIntoView : function(record) {
        var index = this.getIndexByRecord(record);
        if (-1 == index) {
            return;
        }

        this.getView().focusRow(index);
    }
});
