/**
 * @class MP.form.plugin.FieldHint
 * @ptype fieldhint
 * Plugin to display a small help text below or above a form field.
 */

/* http://www.sencha.com/forum/showthread.php?242080-Field-Help-Text-Plugin-for-ExtJS4 */

//jsl:declare Ext

Ext.define('MP.form.plugin.FieldHint', {
    alias: 'plugin.fieldhint',

    /**
     * @cfg {String} [cls='mp-form-fieldhint']
     * CSS Class to apply to the help text element.
     */
    cls: 'mp-form-fieldhint',

    /**
     * @cfg {String} [align='bottom']
     * Text position. Set to 'top' to display the help text above the
     * field, 'bottom' for below.
     */
    align: 'bottom',

    /**
     * @cfg {String} text (required)
     * Help text to display.
     */

    /**
     * @constructor
     * @param {Object/String} config Config object.
     * If this param is a string, it is used as help text. The default
     * values of all other config options are used in this case.
     */
    constructor: function(config) {
        if (Ext.isString(config))
            config = {
                text: config
            };
        Ext.apply(this, config);
    },

    /**
     * Plugin init function
     * @private
     */
    init: function(field) {
        if (!field.isFieldLabelable)
            Ext.Error.raise('FieldHint plugin has to be used on form fields that implement Ext.form.Labelable.');

        // only apply if text available
        if (!Ext.isEmpty(this.text)) {
            var markup = '<div class="' + (this.cls || '') + '">' + this.text + '</div>';
            if (this.align == 'top')
                field.beforeSubTpl = this.getSubTpl(field.beforeSubTpl || '', markup, '');
            else
                field.afterSubTpl = this.getSubTpl(field.afterSubTpl || '', '', markup);
        }
    },

    /**
     * Prepare subTpl
     * @private
     */
    getSubTpl: function(tpl, beforeMarkup, afterMarkup) {
        if (Ext.isString(tpl))
            return beforeMarkup + tpl + afterMarkup;
        else if (!tpl.isTemplate)
            tpl = new Ext.XTemplate(tpl);
        return tpl.set(beforeMarkup + tpl.html + afterMarkup, tpl.compiled);
    }
});
