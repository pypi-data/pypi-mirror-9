//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Model customization
// :Creato:    mer 05 dic 2012 13:12:45 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare console*/


Ext.define("MP.data.Model", {
    override: "Ext.data.Model",

    // Return a dictionary with changed fields (or all fields,
    // if the record is new).
    // If there are no changes, return false. If there is a mandatory
    // field with an empty value, return the field name.
    getModifiedFields: function(idfname, idfvalue) {
        var me = this;
        var data = me.data;
        var fmap = me.fields.map;
        var modified = me.modified;
        var cfields = {};
        var dtype = Ext.data.Types.DATE;

        if(!idfvalue) {
            cfields[idfname] = me.get(idfname);
        } else if(typeof idfvalue == 'function') {
            cfields[idfname] = idfvalue.call(this);
        } else {
            cfields[idfname] = idfvalue;
        }

        // Build a dictionary with changed fields

        var skiprecord = true;
        for (var fname in modified) {
            if(fname != idfname) {
                var field = fmap[fname];

                if (!field || !field.sendBackToServer) {
                    continue;
                }

                var fvalue = data[fname];

                // If it is an empty string, and the original value
                // was "null", skip the field, assuming this is a
                // side effect of editing a null field.

                if(Ext.isEmpty(fvalue)) {
                    if(!field.allowBlank) {
                        // <debug>
                        console.log('Field "' + fname + '" cannot be empty!');
                        // </debug>
                        return fname;
                    }
                    var origvalue = modified && modified[fname];

                    if(Ext.isEmpty(origvalue)) {
                        continue;
                    }
                }
                if (field.serialize) {
                    cfields[fname] = field.serialize(fvalue, me);
                } else if (field.type === dtype && field.dateFormat) {
                    cfields[fname] = Ext.Date.format(fvalue, field.dateFormat);
                } else {
                    cfields[fname] = fvalue;
                }
                skiprecord = false;
            }
        }

        if(skiprecord) {
            return null;
        } else {
            return cfields;
        }
    }
});
