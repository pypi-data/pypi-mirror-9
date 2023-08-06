//-*- coding: utf-8 -*-
//:Progetto:  metapensiero.extjs.desktop -- Form panel customization
//:Creato:    dom 24 nov 2013 14:09:09 CET
//:Autore:    Lele Gaifax <lele@metapensiero.it>
//:Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/

Ext.define('MP.form.Panel', {
    extend: 'Ext.form.Panel',

    requires: ['MP.form.plugin.FieldHint'],

    statics: {
        /**
         * Helper to create a function to setup fields using FieldHint plugin.
         *
         * Example usage:
         *
         *  MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
         *    var editors = metadata.editors({
         *      '*': {
         *        editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%')
         *      }
         *    });
         *    var form = Ext.create('MP.form.Panel', {
         *      fieldDefaults: {
         *        labelWidth: 100,
         *        margin: '15 10 0 10'
         *      },
         *      items: [{
         *        xtype: 'container',
         *        layout: 'hbox',
         *        items: [{
         *          xtype: 'container',
         *          layout: 'anchor',
         *          flex: 1,
         *          items: [
         *            editors.firstField,
         *            editors.secondField
         *          ]
         *        }, {
         *          xtype: 'container',
         *          layout: 'anchor',
         *          flex: 1,
         *          items: [
         *            editors.thirdField,
         *            editors.fourthField
         *          ]
         *        }]
         *      }]
         *    });
         */
        getDefaultEditorSettingsFunction: function(anchor) {
            return function(info) {
                var cfg = { anchor: anchor || '95%' };
                var hint = info.hint || '';

                if(!info.nullable) {
                    cfg.labelClsExtra = 'mp-form-mandatory-field';
                    if(hint !== '') {
                        hint += ' ';
                    }
                    hint += _('[Mandatory]');
                }

                if(hint !== '') {
                    cfg.plugins = [{
                        ptype: 'fieldhint',
                        text: hint
                    }];
                }

                return cfg;
            };
        }
    },

    /**
     * Take into account lookup combos
     */
    updateRecord: function(record) {
        var me = this;

        record = record || this._record;
        if (!record) {
            //<debug>
            Ext.Error.raise("A record is required.");
            //</debug>
            return this;
        }

        var fields = me.getForm().getFields().items;

        record.beginEdit();
        for (var i=0, len=fields.length; i < len; ++i) {
            var field = fields[i];

            if(field.lookupFor) {
                var fname = field.lookupFor;

                if(field.getRawValue() === '') {
                    record.set(fname, null);
                } else if(!Ext.isEmpty(field.lastSelection)) {
                    var iname = field.store.proxy.reader.idProperty;
                    var srec = field.lastSelection[0];
                    var luvalue = srec.get(iname);

                    record.set(fname, luvalue);
                }
            }
        }
        record.endEdit();

        return me.callParent([record]);
    }
});
