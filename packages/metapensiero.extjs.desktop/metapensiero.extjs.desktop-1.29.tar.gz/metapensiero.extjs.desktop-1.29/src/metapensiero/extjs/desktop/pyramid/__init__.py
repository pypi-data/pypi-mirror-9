# -*- coding: utf-8 -*-
#:Progetto:  metapensiero.extjs.desktop -- Pyramid specific stuff
#:Creato:    mar 11 dic 2012 12:45:28 CET
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

from __future__ import absolute_import

import logging

from pyramid.view import view_config
from pyramid.scaffolds import PyramidTemplate
from pyramid.settings import asbool

logger = logging.getLogger(__name__)


class DesktopProjectTemplate(PyramidTemplate):
    _template_dir = 'scaffold'
    summary = 'Barebones ExtJS Desktop'


@view_config(route_name='app',
             renderer='metapensiero.extjs.desktop:templates/app.pt')
def app_view(request):
    # Force a new session
    request.session.invalidate()

    debug = request.registry.settings.get('desktop.debug', False)

    title = request.registry.settings.get('desktop.title', None)
    if title is None:
        logger.warning(u'You should specify “desktop.title” within the'
                       u' [app:main] section of the config file')
        title = 'Desktop'

    version = request.registry.settings.get('desktop.version', None)
    if version is None:
        version = 'dev'

    return {'debug': asbool(debug),
            'app_title': title,
            'app_version': version}


@view_config(route_name='scripts', renderer='json')
def dynamically_loaded_scripts(request):
    from json import load, loads, dump

    output = request.registry.settings.get('desktop.manifest', None)
    if output is None:
        logger.warning(u'You should specify “desktop.manifest” within the'
                       u' [app:main] section of the config file')
        return

    styles = loads(request.params.get('styles', '[]'))

    try:
        with open(output) as f:
            manifest = load(f)
    except IOError:
        manifest = dict(styles=[])

    if manifest.get('styles') != styles:
        manifest['styles'] = styles
        with open(output, 'w') as f:
            dump(manifest, f, indent=2)
        logger.warning(u'Updated sources list in %s', output)


@view_config(route_name='extjs-l10n',
             renderer='metapensiero.extjs.desktop:templates/extjs-l10n.mako')
def extjs_l10n_view(request):
    """
    This view produces a ``Javascript`` source suitable to be included by
    an ExtJS_ application to *override* standard ExtJS messages and labels
    in a gettext compatible way.

    To work properly, it should be included as late as possible.
    """

    request.response.content_type = 'text/javascript'
    name = request.locale_name
    return {'lang': name}


@view_config(route_name='catalog',
             renderer='metapensiero.extjs.desktop:templates/catalog.mako')
def catalog_view(request):
    """
    This view produces the ``Javascript`` source code that implements
    a minimalistic :func:`ngettext` function, conveniently aliased
    to ``_``, and a dictionary containing the translation catalog for
    the request's language.
    """

    from json import dumps

    locale = request.localizer
    name = request.locale_name

    domain = request.registry.settings.get('desktop.domain', None)
    if domain is None:
        logger.warning(u'You should specify “desktop.domain” within the'
                       u' [app:main] section of the config file')
        domain = 'desktop-client'

    try:
        app_catalog = locale.translations._domains[domain]
    except KeyError:
        logger.debug('Could not find "%s" translation catalog for "%s",'
                     ' maybe it has not been compiled? Falling back to'
                     ' the "native" language.', domain, name)
        app_catalog = None

    try:
        desktop_catalog = locale.translations._domains['mp-desktop']
    except KeyError:
        logger.debug('Could not find "%s" translation catalog for "%s",'
                     ' maybe it has not been compiled? Falling back to'
                     ' "native" language.', "mp-desktop", name)
        desktop_catalog = None

    if app_catalog is desktop_catalog is None:
        name = 'en'
        plural_forms = '(n != 1)'
        msgs = {}
    else:
        plural_forms, msgs = _massage_catalog(app_catalog, desktop_catalog)

    request.response.content_type = 'text/javascript'
    return {'domain': domain,
            'plural_forms': plural_forms,
            'lang': name,
            'catalog': dumps(msgs, indent='', separators=(',', ':'),
                             sort_keys=True)}


def _massage_catalog(app_catalog, desktop_catalog):
    """Parse the gettext catalog, extracting needed information.

    :rtype: a tuple of two items, ``(plural-forms-expr, messages)``
    """

    from re import match
    from itertools import chain

    cinfo = (app_catalog or desktop_catalog).info()

    pforms = match(r'\s*nplurals\s*=\s*[0-9]+\s*;\s*'
                   r'plural\s*=\s*(\(.+\))\s*;?\s*$',
                   cinfo['plural-forms'])
    if not pforms:
        raise RuntimeError('Unrecognized plural forms: %s' %
                           cinfo['plural-forms'])

    msgs = {}

    entries = {}
    for m, t in chain(app_catalog._catalog.items()
                      if app_catalog is not None else (),
                      desktop_catalog._catalog.items()
                      if desktop_catalog is not None else ()):
        # Skip the "empty" key, as it is used for the catalog metadata
        if m:
            # Pluralizable messages have (singular,0), (singular,1) and
            # so on as keys for the various plurals. JS dictionaries
            # accept only plain strings as keys, so we use a list of the
            # various forms, ordered by their plurality index and keyed
            # on the singular. In other words, given the following
            # markers::
            #
            #   gettext('Trees')
            #   ngettext('This tree', 'These trees', n)
            #
            # we build a JS dictionary of this kind::
            #
            #   { 'Trees': [ 'Alberi' ],
            #     'This tree': [ 'Questo albero', 'Questi alberi' ]
            #   }
            #
            if isinstance(m, tuple):
                msgid, idx = m
            else:
                msgid = m
                idx = 0
            entries.setdefault(msgid, {})[idx] = t

    for msgid, forms in entries.items():
        indexes = forms.keys()
        msgs[msgid] = [forms[idx] for idx in sorted(indexes)]

    return pforms.group(1), msgs


def configure(config):
    config.add_translation_dirs('metapensiero.extjs.desktop:locale/')
    config.add_static_view('desktop', 'metapensiero.extjs.desktop:assets')

    config.add_route('app', '/')
    config.add_route('catalog', '/catalog')
    config.add_route('extjs-l10n', '/extjs-l10n')
    config.add_route('scripts', '/scripts')

    config.scan('metapensiero.extjs.desktop',
                ignore='metapensiero.extjs.desktop.scripts')
