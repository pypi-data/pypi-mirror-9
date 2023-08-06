//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- A factory of Actions
// :Creato:    lun 26 nov 2012 15:32:15 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/


Ext.define('MP.action.Plugin', {
    extend: 'Ext.AbstractPlugin',

    init: function(component) {
        var me = this;

        me.component = component;

        if(!me.shouldDisableAction && component.shouldDisableAction) {
            me.shouldDisableAction = component.shouldDisableAction.bind(component);
        }
        me.actions = [];
        if(component.plugged_actions === undefined) {
            // Attach the plugged_actions collection and some utilities to
            // the component
            var cactions = component.plugged_actions = new Ext.util.MixedCollection();
            component.getAllActions = function() {
                return cactions.getRange();
            };
            component.findActionById = function(id) {
                return cactions.get(id);
            };
            // Execute the attachActions() method of each plugin providing it
            // just after component's initEvents()
            component.initEvents = Ext.Function.createSequence(component.initEvents, function() {
                if(component.plugins) {
                    Ext.each(component.plugins, function(p) {
                        if(p.attachActions) {
                            p.attachActions();
                        }
                    });
                }
            });
        }
        me.initActions();
    },

    destroy: function() {
        delete this.shouldDisableAction;
        this.callParent(arguments);
    },

    // Override this to create and add the actions
    initActions: Ext.emptyFn,

    // Override this to attach the actions to the UI or to events.
    // This must be called by component's initEvents().
    attachActions: Ext.emptyFn,

    // Add a single action to our list
    addAction: function(act) {
        this.actions.push(act);
        this.component.plugged_actions.add(act.initialConfig.itemId, act);
        return act;
    },

    // Return our list of actions
    getActions: function() {
        return this.actions;
    },

    // Find an action by its itemId, return null if none found.
    findActionById: function(id) {
        var act = null;
        Ext.each(this.getActions(), function(a) {
            if(a.initialConfig.itemId == id) {
                act = a;
                return false;
            }
            return true;
        });
        return act;
    },

    // Update the state of the given action: if the action has a method
    // ``shouldBeDisabled()`` and it returns a boolean value, use that.
    // Otherwise try with ``this.shouldDisableAction()``.
    updateAction: function(act) {
        var disable;

        if(act.shouldBeDisabled) {
            disable = act.shouldBeDisabled();
            if(disable !== null) {
                act.setDisabled(disable);
                return;
            }
        }

        if(this.shouldDisableAction) {
            disable = this.shouldDisableAction(act);
            if(disable !== null) {
                act.setDisabled(disable);
            }
        }
    }
});
