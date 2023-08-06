// -*- mode: js2; coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop
// :Creato:    sab 11 ago 2012 00:07:37 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

//jsl:declare Ext
//jsl:declare _

Ext.onReady(function() {
    var cm = Ext.ClassManager,
        exists = Ext.Function.bind(cm.get, cm);

    if (Ext.Updater) {
        Ext.Updater.defaults.indicatorText =
            '<div class="loading-indicator">' + _('Loading...') + '</div>';
    }

    Ext.define("Ext.locale.${lang}.grid.plugin.DragDrop", {
        override: "Ext.grid.plugin.DragDrop",
        // TRANSLATORS: this is the default text to show while
        // dragging, where {0} is the number of selected items and {1}
        // is empty when number is exactly 1, otherwise the character
        // 's' (to form the English plural form)
        dragText: _("{0} selected row{1}")
    });

    Ext.define("Ext.locale.${lang}.LoadMask", {
        override: "Ext.LoadMask",
        msg: _("Loading...")
    });

    Ext.define("Ext.locale.${lang}.view.AbstractView", {
        override: "Ext.view.AbstractView",
        loadingText: _("Loading...")
    });

    if (Ext.Date) {
        Ext.Date.monthNames = [
            // TRANSLATORS: name of the first month
            _("January"),
            // TRANSLATORS: name of the second month
            _("February"),
            // TRANSLATORS: name of the third month
            _("March"),
            // TRANSLATORS: name of the fourth month
            _("April"),
            // TRANSLATORS: name of the fifth month
            _("May"),
            // TRANSLATORS: name of the sixth month
            _("June"),
            // TRANSLATORS: name of the seventh month
            _("July"),
            // TRANSLATORS: name of the eighth month
            _("August"),
            // TRANSLATORS: name of the nineth month
            _("September"),
            // TRANSLATORS: name of the tenth month
            _("October"),
            // TRANSLATORS: name of the eleventh month
            _("November"),
            // TRANSLATORS: name of the twelfth month
            _("December")];

        Ext.Date.shortMonthNames = [
            // TRANSLATORS: short name of the first month
            _("Jan"),
            // TRANSLATORS: short name of the second month
            _("Feb"),
            // TRANSLATORS: short name of the third month
            _("Mar"),
            // TRANSLATORS: short name of the fourth month
            _("Apr"),
            // TRANSLATORS: short name of the fifth month, remove the
            //“(short)” marker, added only to disambiguate
            _("May (short)"),
            // TRANSLATORS: short name of the sixth month
            _("Jun"),
            // TRANSLATORS: short name of the seventh month
            _("Jul"),
            // TRANSLATORS: short name of the eighth month
            _("Aug"),
            // TRANSLATORS: short name of the nineth month
            _("Sep"),
            // TRANSLATORS: short name of the tenth month
            _("Oct"),
            // TRANSLATORS: short name of the eleventh month
            _("Nov"),
            // TRANSLATORS: short name of the twelfth month
            _("Dec")];

        Ext.Date.getShortMonthName = function(month) {
            return Ext.Date.shortMonthNames[month];
        };

        Ext.Date.monthNumbers = {};
        Ext.Date.monthNumbers[_('January').toLowerCase()] = 0;
        Ext.Date.monthNumbers[_('Jan').toLowerCase()] = 0;
        Ext.Date.monthNumbers[_('February').toLowerCase()] = 1;
        Ext.Date.monthNumbers[_('Feb').toLowerCase()] = 1;
        Ext.Date.monthNumbers[_('March').toLowerCase()] = 2;
        Ext.Date.monthNumbers[_('Mar').toLowerCase()] = 2;
        Ext.Date.monthNumbers[_('April').toLowerCase()] = 3;
        Ext.Date.monthNumbers[_('Apr').toLowerCase()] = 3;
        Ext.Date.monthNumbers[_('May').toLowerCase()] = 4;
        Ext.Date.monthNumbers[_('May (short)').toLowerCase()] = 4;
        Ext.Date.monthNumbers[_('June').toLowerCase()] = 5;
        Ext.Date.monthNumbers[_('Jun').toLowerCase()] = 5;
        Ext.Date.monthNumbers[_('July').toLowerCase()] = 6;
        Ext.Date.monthNumbers[_('Jul').toLowerCase()] = 6;
        Ext.Date.monthNumbers[_('August').toLowerCase()] = 7;
        Ext.Date.monthNumbers[_('Aug').toLowerCase()] = 7;
        Ext.Date.monthNumbers[_('September').toLowerCase()] = 8;
        Ext.Date.monthNumbers[_('Sep').toLowerCase()] = 8;
        Ext.Date.monthNumbers[_('October').toLowerCase()] = 9;
        Ext.Date.monthNumbers[_('Oct').toLowerCase()] = 9;
        Ext.Date.monthNumbers[_('November').toLowerCase()] = 10;
        Ext.Date.monthNumbers[_('Nov').toLowerCase()] = 10;
        Ext.Date.monthNumbers[_('December').toLowerCase()] = 11;
        Ext.Date.monthNumbers[_('Dec').toLowerCase()] = 11;

        Ext.Date.getMonthNumber = function(name) {
            return Ext.Date.monthNumbers[name.toLowerCase()];
        };

        Ext.Date.dayNames = [
            // TRANSLATORS: name of the day “Sunday”
            _("Sunday"),
            // TRANSLATORS: name of the day “Monday”
            _("Monday"),
            // TRANSLATORS: name of the day “Tuesday”
            _("Tuesday"),
            // TRANSLATORS: name of the day “Wednesday”
            _("Wednesday"),
            // TRANSLATORS: name of the day “Thursday”
            _("Thursday"),
            // TRANSLATORS: name of the day “Friday”
            _("Friday"),
            // TRANSLATORS: name of the day “Saturday”
            _("Saturday")];

        Ext.Date.shortDayNames = [
            // TRANSLATORS: short name of the day “Sunday”
            _("Sun"),
            // TRANSLATORS: short name of the day “Monday”
            _("Mon"),
            // TRANSLATORS: short name of the day “Tuesday”
            _("Tue"),
            // TRANSLATORS: short name of the day “Wednesday”
            _("Wed"),
            // TRANSLATORS: short name of the day “Thursday”
            _("Thu"),
            // TRANSLATORS: short name of the day “Friday”
            _("Fri"),
            // TRANSLATORS: short name of the day “Saturday”
            _("Sat")];

        Ext.Date.getShortDayName = function(day) {
            return Ext.Date.shortDayNames[day];
        };
    }

    if (Ext.MessageBox) {
        Ext.apply(Ext.MessageBox, {
            buttonText: {
                ok: _("OK"),
                cancel: _("Cancel"),
                yes: _("Yes"),
                no: _("No")
            },
            titleText: {
                confirm: _('Confirm'),
                prompt: _('Prompt'),
                wait: _('Loading...'),
                alert: _('Attention')
            }
        });
    }

    if (exists('Ext.util.Format')) {
        Ext.apply(Ext.util.Format, {
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
            _("currencyAtEnd")
            ) || 0),
            currencyPrecision: parseInt(
            // TRANSLATORS: this is the number of decimal places used
            // to format currency values, must be an integer value
            _("currencyPrecision")
            ) || 2,
            // TRANSLATORS: this is a date format, see
            // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
            dateFormat: _("m/d/Y")
        });
    }

    Ext.define("Ext.locale.${lang}.picker.Date", {
        override: "Ext.picker.Date",
        todayText: _("Today"),
        minText: _("This date is before the minimum date"),
        maxText: _("This date is after the maximum date"),
        disabledDaysText: _("Disabled"),
        disabledDatesText: _("Disabled"),
        monthNames: Ext.Date.monthNames,
        dayNames: Ext.Date.dayNames,
        nextText: _("Next Month (Control+Right)"),
        prevText: _("Previous Month (Control+Left)"),
        monthYearText: _("Choose a month (Control+Up/Down to move years)"),
        // TRANSLATORS: this is a date format, see
        // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
        monthYearFormat: _("F Y"),
        todayTip: _("{0} (Spacebar)"),
        // TRANSLATORS: this is a short date format, see
        // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
        format: _("m/d/y"),
        // TRANSLATORS: this is a date format, see
        // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
        longDayFormat: _("F d, Y"),
        startDay: parseInt(
        // TRANSLATORS: this is the "index" of the first day of the week
        // 0 means Sunday, 1 Monday and so on.
        _("startDay")
        ) || 0
    });

    Ext.define("Ext.locale.${lang}.picker.Month", {
        override: "Ext.picker.Month",
        okText: _("&#160;OK&#160;"),
        cancelText: _("Cancel")
    });

    Ext.define("Ext.locale.${lang}.toolbar.Paging", {
        override: "Ext.PagingToolbar",
        beforePageText: _("Page"),
        // TRANSLATORS: this is the text that goes after the current page number,
        // where {0} is the total number of pages
        afterPageText: _("of {0}"),
        firstText: _("First Page"),
        prevText: _("Previous Page"),
        nextText: _("Next Page"),
        lastText: _("Last Page"),
        refreshText: _("Refresh"),
        // TRANSLATORS: this is the description of current records range, where
        // {0} is the start record index, {1} the end record index and {2} the
        // total number of records
        displayMsg: _("Displaying {0} - {1} of {2}"),
        emptyMsg: _("No data to display")
    });

    Ext.define("Ext.locale.${lang}.form.Basic", {
        override: "Ext.form.Basic",
        waitTitle: _("Please Wait...")
    });

    Ext.define("Ext.locale.${lang}.form.field.Base", {
        override: "Ext.form.field.Base",
        invalidText: _("The value in this field is invalid")
    });

    Ext.define("Ext.locale.${lang}.form.field.Text", {
        override: "Ext.form.field.Text",
        minLengthText: _("The minimum length for this field is {0}"),
        maxLengthText: _("The maximum length for this field is {0}"),
        blankText: _("This field is required")
    });

    Ext.define("Ext.locale.${lang}.form.field.Number", {
        override: "Ext.form.field.Number",
        // TRANSLATORS: this is the character used as decimal separator, "."
        decimalSeparator: _("decimalSeparator"),
        decimalPrecision: parseInt(
        // TRANSLATORS: this is the number of decimal digits
        _("decimalPrecision")
        ) || 2,
        minText: _("The minimum value for this field is {0}"),
        maxText: _("The maximum value for this field is {0}"),
        nanText: _("{0} is not a valid number")
    });

    Ext.define("Ext.locale.${lang}.form.field.Date", {
        override: "Ext.form.field.Date",
        disabledDaysText: _("Disabled"),
        disabledDatesText: _("Disabled"),
        minText: _("The date in this field must be after {0}"),
        maxText: _("The date in this field must be before {0}"),
        invalidText: _("{0} is not a valid date - it must be in the format {1}"),
        // TRANSLATORS: this is a date format, see
        // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
        format: _("m/d/y"),
        // TRANSLATORS: this is a |-separated list of recognized date formats
        altFormats: _("m/d/Y|m-d-y|m-d-Y|m/d|m-d|md|mdy|mdY|d|Y-m-d"),
        startDay: parseInt(
        // TRANSLATORS: this is the "index" of the first day of the week
        // 0 means Sunday, 1 Monday and so on.
        _("startDay")
        ) || 0
    });

    if (exists('Ext.form.field.VTypes')) {
        Ext.apply(Ext.form.field.VTypes, {
            emailText: (_('This field should be an email address in the format')
                        + ' "'
                        // TRANSLATORS: this is just an example of an email address
                        + _('user@example.com')
                        , '"'),
            urlText: (_('This field should be a URL in the format')
                      + ' "http://'
                      // TRANSLATORS: this is just an example of an HTTP host name
                      + _('www.example.com')
                      + '"'),
            alphaText: _('This field should only contain letters and _'),
            alphanumText: _('This field should only contain letters, numbers and _')
        });
    }

    Ext.define("Ext.locale.${lang}.form.field.HtmlEditor", {
        override: "Ext.form.field.HtmlEditor",
        createLinkText: _('Please enter the URL for the link:')
    }, function() {
        Ext.apply(Ext.form.field.HtmlEditor.prototype, {
            buttonTips: {
                bold: {
                    title: 'Bold (Ctrl+B)',
                    text: 'Make the selected text bold.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                italic: {
                    title: 'Italic (Ctrl+I)',
                    text: 'Make the selected text italic.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                underline: {
                    title: 'Underline (Ctrl+U)',
                    text: 'Underline the selected text.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                increasefontsize: {
                    title: 'Grow Text',
                    text: 'Increase the font size.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                decreasefontsize: {
                    title: 'Shrink Text',
                    text: 'Decrease the font size.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                backcolor: {
                    title: 'Text Highlight Color',
                    text: 'Change the background color of the selected text.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                forecolor: {
                    title: 'Font Color',
                    text: 'Change the color of the selected text.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                justifyleft: {
                    title: 'Align Text Left',
                    text: 'Align text to the left.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                justifycenter: {
                    title: 'Center Text',
                    text: 'Center text in the editor.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                justifyright: {
                    title: 'Align Text Right',
                    text: 'Align text to the right.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                insertunorderedlist: {
                    title: 'Bullet List',
                    text: 'Start a bulleted list.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                insertorderedlist: {
                    title: 'Numbered List',
                    text: 'Start a numbered list.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                createlink: {
                    title: 'Hyperlink',
                    text: 'Make the selected text a hyperlink.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                },
                sourceedit: {
                    title: 'Source Edit',
                    text: 'Switch to source editing mode.',
                    cls: Ext.baseCSSPrefix + 'html-editor-tip'
                }
            }
        });
    });

    Ext.define("Ext.locale.${lang}.grid.header.Container", {
        override: "Ext.grid.header.Container",
        sortAscText: _("Sort Ascending"),
        sortDescText: _("Sort Descending"),
        columnsText: _("Columns")
    });

    Ext.define("Ext.locale.${lang}.grid.GroupingFeature", {
        override: "Ext.grid.GroupingFeature",
        // TRANSLATORS: this the "empty group" text
        emptyGroupText: _("(None)"),
        groupByText: _("Group By This Field"),
        showGroupsText: _("Show in Groups")
    });

    Ext.define("Ext.locale.${lang}.grid.PropertyColumnModel", {
        override: "Ext.grid.PropertyColumnModel",
        nameText: _("Name"),
        valueText: _("Value"),
        // TRANSLATORS: this is a date format, see
        // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
        dateFormat: _("m/j/Y"),
        trueText: _("true"),
        falseText: _("false")
    });

    Ext.define("Ext.locale.${lang}.grid.BooleanColumn", {
        override: "Ext.grid.BooleanColumn",
        trueText: _("true"),
        falseText: _("false"),
        // TRANSLATORS: this is the undefined value for a boolean column
        undefinedText: _("&#160;")
    });

    Ext.define("Ext.locale.${lang}.grid.NumberColumn", {
        override: "Ext.grid.NumberColumn",
        // TRANSLATORS: this is the format used to format a number column
        format: _('0,000.00')
    });

    Ext.define("Ext.locale.${lang}.grid.DateColumn", {
        override: "Ext.grid.DateColumn",
        // TRANSLATORS: this is a date format, see
        // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
        format: _("m/d/Y")
    });

    Ext.define("Ext.locale.${lang}.grid.ActionColumn", {
        override: "Ext.grid.ActionColumn",
        menuText: _("<i>Actions</i>")
    });

    Ext.define("Ext.locale.${lang}.form.field.Time", {
        override: "Ext.form.field.Time",
        minText: _("The time in this field must be equal to or after {0}"),
        maxText: _("The time in this field must be equal to or before {0}"),
        invalidText: _("{0} is not a valid time"),
        // TRANSLATORS: this is a time format, see
        // http://docs.sencha.com/extjs/4.2.1/#!/api/Ext.Date
        format: _("g:i A"),
        // TRANSLATORS: this is a |-separated list of recognized time formats
        altFormats: _("g:ia|g:iA|g:i a|g:i A|h:i|g:i|H:i|ga|ha|gA|h a|g a|g A|gi|hi|gia|hia|g|H")
    });

    Ext.define("Ext.locale.${lang}.form.CheckboxGroup", {
        override: "Ext.form.CheckboxGroup",
        blankText: _("You must select at least one item in this group")
    });

    Ext.define("Ext.locale.${lang}.form.RadioGroup", {
        override: "Ext.form.RadioGroup",
        blankText: _("You must select one item in this group")
    });
});
