/*jsl:declare Ext*/
/*jsl:declare _*/

/**
 * The main upload dialog.
 *
 * Mostly, this will be the only object you need to interact
 * with. Just initialize it and show it:
 *
 *      @example
 *      var dialog = Ext.create('MP.upload.Dialog', {
 *          dialogTitle: 'My Upload Widget',
 *          uploadUrl: 'upload.php'
 *      });
 *
 *      dialog.show();
 *
 */
Ext.define('MP.upload.Dialog', {
    extend : 'Ext.window.Window',

    requires : [
        'MP.upload.ItemGridPanel',
        'MP.upload.Manager',
        'MP.upload.StatusBar',
        'MP.upload.BrowseButton',
        'MP.upload.Queue'
    ],

    /**
     * @cfg {Number} [width=700]
     */
    width : 700,

    /**
     * @cfg {Number} [height=500]
     */
    height : 500,

    config : {
        /**
         * @cfg {String}
         *
         * The title of the dialog.
         */
        dialogTitle : '',

        /**
         * @cfg {boolean} [synchronous=false]
         *
         * If true, all files are uploaded in a sequence, otherwise
         * files are uploaded simultaneously (asynchronously).
         */
        synchronous : true,

        /**
         * @cfg {String} uploadUrl (required)
         *
         * The URL to upload files to.
         */
        uploadUrl : '',

        /**
         * @cfg {Object}
         *
         * Params passed to the uploader object and sent along with
         * the request. It depends on the implementation of the
         * uploader object, for example if the {@link
         * MP.upload.ExtJsUploader} is used, the params
         * are sent as GET params.
         */
        uploadParams : {},

        /**
         * @cfg {Object}
         *
         * Extra HTTP headers to be added to the HTTP request uploading the file.
         */
        uploadExtraHeaders : {},

        /**
         * @cfg {Number} [uploadTimeout=6000]
         *
         * The time after the upload request times out - in miliseconds.
         */
        uploadTimeout : 6000,

        // dialog strings
        textOk : _('OK'),
        textClose : _('Close'),
        textUpload : _('Upload'),
        textAbort : _('Abort'),
        textRemoveSelected : _('Remove selected'),
        textRemoveAll : _('Remove all'),

        multiSelect : true
    },

    /**
     * @property {MP.upload.Queue}
     */
    queue : null,

    /**
     * @property {MP.upload.ItemGridPanel}
     */
    grid : null,

    /**
     * @property {MP.upload.Manager}
     */
    uploadManager : null,

    /**
     * @property {MP.upload.StatusBar}
     */
    statusBar : null,

    /**
     * @property {MP.upload.BrowseButton}
     */
    browseButton : null,

    /**
     * Constructor.
     */
    constructor : function(config) {
        this.initConfig(config);

        return this.callParent(arguments);
    },

    /**
     * @private
     */
    initComponent : function() {

        this.addEvents({
            /**
             * @event
             *
             * Fired when all files has been processed.
             *
             * @param {MP.upload.Dialog} dialog
             * @param {MP.upload.Manager} manager
             * @param {MP.upload.Item[]} items
             * @param {Number} errorCount
             */
            uploadcomplete : true
        });

        this.queue = this.initQueue();

        this.initGrid();

        this.initManager();

        this.uploadManager.on('uploadcomplete', this.onUploadComplete, this);
        this.uploadManager.on('itemuploadsuccess', this.onItemUploadSuccess, this);
        this.uploadManager.on('itemuploadfailure', this.onItemUploadFailure, this);

        this.statusBar = Ext.create('MP.upload.StatusBar', {
            dock : 'bottom',
            selectionMessageText : this.selectionMessageText,
            uploadMessageText : this.uploadMessageText
        });

        Ext.apply(this, {
            title : this.dialogTitle,
            autoScroll : true,
            layout : 'fit',
            uploading : false,
            items : [
                this.grid
            ],
            dockedItems : [
                this.getTopToolbarConfig(),
                {
                    xtype : 'toolbar',
                    dock : 'bottom',
                    ui : 'footer',
                    defaults : {
                        minWidth : this.minButtonWidth
                    },
                    items : [
                        '->',
                        {
                            text : this.textClose,
                            // iconCls : 'mp-upload-icon-action-ok',
                            cls : 'x-btn-text-icon',
                            scope : this,
                            handler : function() {
                                this.close();
                            }
                        }
                    ]
                },
                this.statusBar
            ]
        });

        this.on('afterrender', function() {
            this.stateInit();
        }, this);

        this.callParent(arguments);
    },

    initGrid : function() {
        this.grid = Ext.create('MP.upload.ItemGridPanel', {
            queue : this.queue
        });
    },

    initManager : function() {
        this.uploadManager = Ext.create('MP.upload.Manager', {
            url : this.uploadUrl,
            synchronous : this.synchronous,
            params : this.uploadParams,
            extraHeaders : this.uploadExtraHeaders,
            uploadTimeout : this.uploadTimeout
        });
    },

    /**
     * @private
     *
     * Returns the config object for the top toolbar.
     *
     * @return {Array}
     */
    getTopToolbarConfig : function() {
        this.browseButton = Ext.create('MP.upload.BrowseButton', {
            id : 'button_browse',
            multiSelect : this.multiSelect
        });
        this.browseButton.on('fileselected', this.onFileSelection, this);

        return {
            xtype : 'toolbar',
            dock : 'top',
            items : [
                this.browseButton,
                '-',
                {
                    id : 'button_upload',
                    text : this.textUpload,
                    iconCls : 'mp-upload-icon-action-upload',
                    scope : this,
                    handler : this.onInitUpload
                },
                '-',
                {
                    id : 'button_abort',
                    text : this.textAbort,
                    iconCls : 'mp-upload-icon-action-abort',
                    scope : this,
                    handler : this.onAbortUpload,
                    disabled : true
                },
                '->',
                {
                    id : 'button_remove_selected',
                    text : this.textRemoveSelected,
                    iconCls : 'mp-upload-icon-action-remove',
                    scope : this,
                    handler : this.onMultipleRemove
                },
                '-',
                {
                    id : 'button_remove_all',
                    text : this.textRemoveAll,
                    iconCls : 'mp-upload-icon-action-remove',
                    scope : this,
                    handler : this.onRemoveAll
                }
            ]
        };
    },

    /**
     * @private
     *
     * Initializes and returns the queue object.
     *
     * @return {MP.upload.Queue}
     */
    initQueue : function() {
        var queue = Ext.create('MP.upload.Queue');

        queue.on('queuechange', this.onQueueChange, this);

        return queue;
    },

    onInitUpload : function() {
        if (!this.queue.getCount()) {
            return;
        }

        this.stateUpload();
        this.startUpload();
    },

    onAbortUpload : function() {
        this.uploadManager.abortUpload();
        this.finishUpload();
        this.switchState();
    },

    onUploadComplete : function(manager, queue, errorCount) {
        this.finishUpload();
        this.stateInit();
        this.fireEvent('uploadcomplete', this, manager,
                       queue.getUploadedItems(), errorCount);
    },

    /**
     * @private
     *
     * Executes after files has been selected for upload through the
     * "Browse" button. Updates the upload queue with the new files.
     *
     * @param {MP.upload.BrowseButton} input
     * @param {FileList} files
     */
    onFileSelection : function(input, files) {
        //jsl:unused input
        this.queue.clearUploadedItems();
        this.queue.addFiles(files);
        this.browseButton.reset();
    },

    /**
     * @private
     *
     * Executes if there is a change in the queue. Updates the related
     * components (grid, toolbar).
     *
     * @param {MP.upload.Queue} queue
     */
    onQueueChange : function(/*queue*/) {
        this.updateStatusBar();

        this.switchState();
    },

    /**
     * @private
     *
     * Executes upon hitting the "multiple remove" button. Removes all
     * selected items from the queue.
     */
    onMultipleRemove : function() {
        var records = this.grid.getSelectedRecords();
        if (!records.length) {
            return;
        }

        var keys = [];
        var i;
        var num = records.length;

        for (i = 0; i < num; i++) {
            keys.push(records[i].get('filename'));
        }

        this.queue.removeItemsByKey(keys);
        this.grid.getSelectionModel().toggleUiHeader(false);
    },

    onRemoveAll : function() {
        this.queue.clearItems();
        this.grid.getSelectionModel().toggleUiHeader(false);
    },

    onItemUploadSuccess : function(/*item, info*/) {

    },

    onItemUploadFailure : function(/*item, info*/) {

    },

    startUpload : function() {
        this.uploading = true;
        this.uploadManager.uploadQueue(this.queue);
    },

    finishUpload : function() {
        this.uploading = false;
    },

    isUploadActive : function() {
        return this.uploading;
    },

    updateStatusBar : function() {
        if (!this.statusBar) {
            return;
        }

        var numFiles = this.queue.getCount();

        this.statusBar.setSelectionMessage(numFiles, this.queue.getTotalBytes());
    },

    getButton : function(id) {
        return Ext.ComponentMgr.get(id);
    },

    switchButtons : function(info) {
        var id;
        for (id in info) {
            this.switchButton(id, info[id]);
        }
    },

    switchButton : function(id, on) {
        var button = this.getButton(id);

        if (button) {
            if (on) {
                button.enable();
            } else {
                button.disable();
            }
        }
    },

    switchState : function() {
        if (this.uploading) {
            this.stateUpload();
        } else if (this.queue.getCount()) {
            this.stateQueue();
        } else {
            this.stateInit();
        }
    },

    stateInit : function() {
        this.switchButtons({
            button_browse : this.multiSelect ? 1 : !this.queue.getCount(),
            button_upload : 0,
            button_abort : 0,
            button_remove_all : 1,
            button_remove_selected : 1
        });
    },

    stateQueue : function() {
        this.switchButtons({
            button_browse : this.multiSelect ? 1 : !this.queue.getCount(),
            button_upload : 1,
            button_abort : 0,
            button_remove_all : 1,
            button_remove_selected : 1
        });
    },

    stateUpload : function() {
        this.switchButtons({
            button_browse : 0,
            button_upload : 0,
            button_abort : 1,
            button_remove_all : 1,
            button_remove_selected : 1
        });
    }
});
