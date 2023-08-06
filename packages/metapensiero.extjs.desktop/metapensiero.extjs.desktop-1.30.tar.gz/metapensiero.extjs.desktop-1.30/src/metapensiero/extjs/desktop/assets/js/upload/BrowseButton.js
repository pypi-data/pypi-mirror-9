/*jsl:declare Ext*/
/*jsl:declare _*/

/**
 * A "browse" button for selecting multiple files for upload.
 *
 */
Ext.define('MP.upload.BrowseButton', {
    extend : 'Ext.form.field.File',

    buttonOnly : true,

    iconCls : 'mp-upload-icon-action-browse',
    buttonText : _('Browse…'),

    /**
     * @cfg {Boolean} multiSelect
     * Whether the file selector allows multiple selections
     */
    multiSelect: true,

    initComponent : function() {
        this.addEvents({
            fileselected: true
        });

        Ext.apply(this, {
            buttonConfig : {
                iconCls : this.iconCls,
                text : this.buttonText
            }
        });

        if(this.multiSelect) {
            this.on('afterrender', function() {
                // Allow picking multiple files at once.
                this.fileInputEl.dom.setAttribute('multiple', '1');
            }, this);
        }

        this.on('change', function() {
            var files = this.fileInputEl.dom.files;
            if (files) {
                this.fireEvent('fileselected', this, files);
            }
        }, this);

        this.callParent(arguments);
    }
});
