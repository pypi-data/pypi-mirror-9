//  -*- mode: js; coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop
// :Creato:    ven 10 ago 2012 23:37:05 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

_l10n_ = {};
_l10n_.domain = "${domain | n}";
_l10n_.lang = "${lang | n}";
_l10n_.catalog = ${catalog | n};
_l10n_.plural_form = new Function("n", "var form = ${plural_forms}; return form === true ? 1 : (form === false ? 0 : form);");
_l10n_.ngettext = function(singular, plural, count) {
    var form, forms = _l10n_.catalog[singular];
    if(forms === undefined) {
        if(plural === undefined) {
            return singular;
        } else {
            form = _l10n_.plural_form(count);
            return (form === 0 ? singular : plural);
        }
    } else {
        if(plural === undefined) {
            return forms[0] || singular;
        } else {
            form = _l10n_.plural_form(count);
            return forms[form] || (form === 0 ? singular : plural);
        }
    }
};
_ = gettext = ngettext = _l10n_.ngettext;
N_ = function(x) {return x;};
