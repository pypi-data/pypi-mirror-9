/*jsl:declare Ext*/

Ext.define('MP.upload.Store', {
    extend : 'Ext.data.Store',

    fields : [
        {
            name : 'filename',
            type : 'string'
        }, {
            name : 'size',
            type : 'integer'
        }, {
            name : 'contenttype',
            type : 'string'
        }, {
            name : 'status',
            type : 'string'
        }, {
            name : 'message',
            type : 'string'
        }
    ],

    proxy : {
        type : 'memory',
        reader : {
            type : 'array',
            idProperty : 'filename'
        }
    }
});
