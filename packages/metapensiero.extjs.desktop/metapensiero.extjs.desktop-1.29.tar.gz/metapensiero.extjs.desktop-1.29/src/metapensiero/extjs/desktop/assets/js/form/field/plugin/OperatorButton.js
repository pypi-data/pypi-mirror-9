/**
 * @class MP.form.field.field.OperatorButton
 *
 * Plugin for text components that shows a "operator" button over the
 * text field and shows a menu with operators.
 * For use in MP.grid.plugin.FilterBar plugin
 * 2012-07-30 by Ing. Leonardo D'Onofrio (leonardo_donofrio at hotmail.com)
 */

/*jsl:declare Ext*/
/*jsl:declare _*/

Ext.define('MP.form.field.plugin.OperatorButton', {
    extend: 'Ext.AbstractPlugin',
    alias: 'plugin.operatorbutton',
    mixins: {
        observable: 'Ext.util.Observable'
    },

    autoHide: true,

    operatorButtonCls: 'mp-operator-button',

    operator: 'like',

    textField: undefined,
    operatorSet: {
        eq: {
            text: _('Is equal to'),
            iconCls: 'mp-operator-button-eq',
            value: '='
        },
        ne: {
            text: _('Is not equal to'),
            iconCls: 'mp-operator-button-ne',
            value: '<>'
        },
        gte: {
            text: _('Greater than or equal'),
            iconCls: 'mp-operator-button-gte',
            value: '>='
        },
        lte: {
            text: _('Less than or equal'),
            iconCls: 'mp-operator-button-lte',
            value: '<='
        },
        gt: {
            text: _('Greater than'),
            iconCls: 'mp-operator-button-gt',
            value: '>'
        },
        lt: {
            text: _('Less than'),
            iconCls: 'mp-operator-button-lt',
            value: '<'
        },
        like: {
            text: _('Contains'),
            iconCls: 'mp-operator-button-like',
            value: '~'
        },
        start: {
            text: _('Starts with'),
            iconCls: 'mp-operator-button-start',
            value: '~='
        }
    },

    constructor: function(config) {
        var me = this;

        if(config.operator) {
            if(!me.operatorSet[config.operator]) {
                var opset = me.operatorSet;
                for(var op in opset) {
                    if(opset.hasOwnProperty(op) && opset[op].value == config.operator) {
                        config.operator = op;
                        break;
                    }
                };
            }
        }

        Ext.apply(me, config);
        me.mixins.observable.constructor.call(me);
        me.callParent(arguments);
    },

    init: function(textField) {
        var me = this,
            items = [],
            oporder = ['like', 'eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'start'];

        me.operator = me.operatorSet[me.operator] ? me.operator : 'like';
        me.task = Ext.create('Ext.util.DelayedTask');

        for(var i=0, l=oporder.length; i<l; i++) {
            items.push(Ext.apply(Ext.clone(me.operatorSet[oporder[i]]), {
                handler: me.onOperatorClick,
                scope: me
            }));
        }

        me.textField = textField;
        me.menu = Ext.create('Ext.menu.Menu', {
            items: items,
            listeners: {
                hide: me.onMenuHide,
                scope: me
            }
        });
        if (!textField.rendered) {
            textField.on('afterrender', me.onFieldRender, me, { single: true });
        } else {
            me.onFieldRender();
        }
        me.addEvents('operatorchanged');
        textField.addEvents('operatorchanged');
        textField.on({
            destroy: me.onFieldDestroy,
            focus: me.onFieldFocus,
            blur: me.onFieldBlur,
            resize: me.onFieldResize,
            scope: me
        });
    },

    onFieldRender: function(textField) {
        //jsl:unused textField
        var me = this,
        bodyEl = me.textField.bodyEl,
        btn;

        btn = me.operatorButtonEl = me.textField.bodyEl.createChild({
            tag: 'div',
            cls: me.operatorButtonCls + ' ' + me.operatorSet[me.operator].iconCls,
            style: 'visibility: hidden;',
            'data-qtip': me.operatorSet[me.operator].text
        });

        bodyEl.on('mouseover', me.onFieldMouseOver, me);
        bodyEl.on('mouseout', me.onFieldMouseOut, me);
        btn.on('mouseover', me.onButtonMouseOver, me);
        btn.on('mouseout', me.onButtonMouseOut, me);
        btn.on('click', me.onButtonClick, me);

        me.repositionOperatorButton();
        me.updateOperatorButtonVisibility();
    },

    onFieldDestroy: function() {
        var me = this;

        me.operatorButtonEl.destroy();
        me.menu.destroy();
    },

    onFieldFocus: function() {
        var me = this;

        me.fieldInFocus = true;
        me.updateOperatorButtonVisibility();
    },

    onFieldBlur: function() {
        var me = this;

        me.fieldInFocus = false;
        me.updateOperatorButtonVisibility();
    },

    onFieldResize: function() {
        var me = this;

        me.repositionOperatorButton();
    },

    onFieldMouseOver: function(e) {
        var me = this;

        if (me.textField.triggerEl) {
            if (e.getRelatedTarget() == me.textField.triggerEl.elements[0].dom) {
                return;
            }
        }
        me.operatorButtonEl.addCls(me.operatorButtonCls + '-mouse-over-input');
        if (e.getRelatedTarget() == me.operatorButtonEl.dom) {
            // Moused moved to operator button and will generate another mouse event there.
            // Handle it here to avoid duplicate updates (else animation will break)
            me.operatorButtonEl.removeCls(me.operatorButtonCls + '-mouse-over-button');
            me.operatorButtonEl.removeCls(me.operatorButtonCls + '-mouse-down');
        }
        me.updateOperatorButtonVisibility();
    },

    onFieldMouseOut: function(e) {
        var me = this;

        if (me.textField.triggerEl) {
            if (e.getRelatedTarget() == me.textField.triggerEl.elements[0].dom) {
                return;
            }
        }
        me.operatorButtonEl.removeCls(me.operatorButtonCls + '-mouse-over-input');
        if (e.getRelatedTarget() == me.operatorButtonEl.dom) {
            // Moused moved from operator button and will generate another mouse event there.
            // Handle it here to avoid duplicate updates (else animation will break)
            me.operatorButtonEl.addCls(me.operatorButtonCls + '-mouse-over-button');
        }
        me.updateOperatorButtonVisibility();
    },

    onButtonMouseOver: function(e) {
        var me = this;

        e.stopEvent();
        if (me.textField.bodyEl.contains(e.getRelatedTarget())) {
            // has been handled in handleMouseOutOfInputField() to prevent double update
            return;
        }
        me.operatorButtonEl.addCls(me.operatorButtonCls + '-mouse-over-button');
        me.updateOperatorButtonVisibility();
    },

    onButtonMouseOut: function(e) {
        var me = this;

        e.stopEvent();
        if (me.textField.bodyEl.contains(e.getRelatedTarget())) {
            // will be handled in handleMouseOverInputField() to prevent double update
            return;
        }
        me.operatorButtonEl.removeCls(me.operatorButtonCls + '-mouse-over-button');
        me.operatorButtonEl.removeCls(me.operatorButtonCls + '-mouse-down');
        me.updateOperatorButtonVisibility();
    },

    onButtonClick: function(e) {
        var me = this;

        if (e.button !== 0) return;
        me.menu.showAt(e.getX(), e.getY(), false);
        e.stopEvent();
    },

    onOperatorClick: function(item) {
        var me = this,
            opset = me.operatorSet,
            btn = me.operatorButtonEl,
            field = me.textField,
            lastOperator = me.operator;

        for(var op in opset) {
            if(opset.hasOwnProperty(op))
                btn.removeCls(opset[op].iconCls);
        };
        btn.addCls(item.iconCls);
        btn.set({
            'data-qtip': item.text
        });

        me.operator = item.value;
        field.operator = item.value;
        field.focus();
        if (lastOperator != me.operator) {
            me.textField.fireEvent('operatorchanged',
                                   me.textField, me.operator, lastOperator);
            me.fireEvent('operatorchanged',
                         me.textField, me.operator, lastOperator);
        }
    },

    onMenuHide: function() {
        var me = this;

        me.updateOperatorButtonVisibility();
    },

    shouldButtonBeVisible: function() {
        var me = this;

        if (me.autoHide
            && !me.menu.isVisible()
            && !me.fieldInFocus
            && !me.operatorButtonEl.hasCls(me.operatorButtonCls + '-mouse-over-button')
            && !me.operatorButtonEl.hasCls(me.operatorButtonCls + '-mouse-over-input')) {
            return false;
        }
        return true;
    },

    updateOperatorButtonVisibility: function() {
        var me = this, btn = me.operatorButtonEl, padding;
        var newVisible = me.shouldButtonBeVisible();

        if (!Ext.isWebKit) {
            padding = (newVisible ? 18 : 0);
        } else {
            padding = (newVisible || !me.webKitBugFlag ? 18 : 0);
            me.webKitBugFlag = true;
        }
        me.textField.inputEl.applyStyles({
            'padding-left': padding + 'px'
        });

        //if (oldVisible == newVisible) return;

        me.task.delay(200, function() {
            var oldVisible = btn.isVisible();

            if (oldVisible == newVisible) return;

            btn.stopAnimation();
            btn.setVisible(newVisible, {
                duration: 0
            });

            if (!Ext.isWebKit) {
                padding = (newVisible ? 18 : 0);
            } else {
                padding = (newVisible || !me.webKitBugFlag ? 18 : 0);
                me.webKitBugFlag = true;
            }
            me.textField.inputEl.applyStyles({
                'padding-left': padding + 'px'
            });
        });
    },

    repositionOperatorButton: function() {
        var me = this,
        btn = me.operatorButtonEl;

        if (!btn) return;
        btn.alignTo(this.textField.bodyEl, 'tl-tl', [2, 4]);
    }
});
