// -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Specialized field to money amounts
// :Creato:    sab 02 nov 2013 16:46:51 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/
/*jsl:declare _*/

/*
 * TODO: it would be nice to reformat the content of the field *while*
 * the user edits it, but it's not as easy as it sounds; for example
 * the following is a simplicistic approach:
 *
 *    onChange: function() {
 *       this.setRawValue(this.valueToRaw(this.getValue()));
 *       this.callParent(arguments);
 *   },
 *
 * but then the hardest thing is to reposition the "caret" after each
 * "redraw".
 */

Ext.define('MP.form.field.CurrencyField', {
    extend: 'Ext.form.field.Number',
    alias: 'widget.currencyfield',

    // TRANSLATORS: this is the character used as thousand separator, ","
    thousandSeparator: _("thousandSeparator"),
    // TRANSLATORS: this is the character used as decimal separator, "."
    decimalSeparator: _("decimalSeparator"),
    // TRANSLATORS: this is the character used as currency sign, "$"
    currencySign: _("currencySign"),
    currencyAtEnd: !!(parseInt(
        // TRANSLATORS: this determines the position of the currency sign,
        // "0" (zero) means it will be inserted at the beginning, with
        // any other integer value it will be appended to the formatted
        // value.
        _("currencyAtEnd"), 10) || 0),
    currencyPrecision: parseInt(
        // TRANSLATORS: this is the number of decimal places used
        // to format currency values, must be an integer value
        _("currencyPrecision"), 10) || 2,

    fieldStyle: 'text-align: right;',

    parseValue: function(value) {
        if(!Ext.isEmpty(value)) {
            value = String(value).replace(this.currencySign, '');
            value = value.replace(this.thousandSeparator, '');
        }
        return this.callParent([value]);
    },

    valueToRaw: function(value) {
        var sign = this.currencyAtEnd
            ? (" " + this.currencySign)
            : (this.currencySign + " ");
        return Ext.util.Format.currency(value,
                                        sign,
                                        this.currencyPrecision,
                                        this.currencyAtEnd);
    },

    getErrors: function(value) {
        if(!Ext.isEmpty(value)) {
            value = String(value).replace(this.currencySign, '');
            value = value.replace(this.thousandSeparator, '');
        }
        return this.callParent([value]);
    }
});
