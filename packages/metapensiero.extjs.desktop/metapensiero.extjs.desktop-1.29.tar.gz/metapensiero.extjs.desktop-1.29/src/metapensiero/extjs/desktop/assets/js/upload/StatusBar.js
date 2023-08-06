/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare ngettext*/

/**
 * Upload status bar.
 *
 * @class MP.upload.StatusBar
 * @extends Ext.toolbar.Toolbar
 */
Ext.define('MP.upload.StatusBar', {
    extend : 'Ext.toolbar.Toolbar',

    config : {
        textComponentId : 'mu-status-text'
    },

    constructor : function(config) {
        this.initConfig(config);

        return this.callParent(arguments);
    },

    initComponent : function() {
        Ext.apply(this, {
            items : [
                {
                    xtype : 'tbtext',
                    id : this.textComponentId,
                    text : '&nbsp;'
                }
            ]
        });

        this.callParent(arguments);
    },

    setText : function(text) {
        this.getComponent(this.textComponentId).setText(text);
    },

    setSelectionMessage : function(fileCount, byteCount) {
        this.setText(Ext.String.format(
            // TRANSLATORS: {0} is the number of files, {1} the total size
            ngettext('Selected {0} file, {1}',
                     'Selected {0} files, {1}',
                     fileCount),
            fileCount, Ext.util.Format.fileSize(byteCount)));
    },

    setUploadMessage : function(progressPercent, uploadedFiles, totalFiles) {
        this.setText(Ext.String.format(
            // TRANSLATORS: {0} is the completion percentage, {1} the number of
            // uploaded files, {2} the total number of files
            ngettext('Upload progress {0}% ({1} of {2} file)',
                     'Upload progress {0}% ({1} of {2} files)',
                     totalFiles),
            progressPercent, uploadedFiles, totalFiles));
    }

});
