# -*- coding: utf-8 -*-
#:Progetto:  SoL -- i18n utilities
#:Creato:    mer 10 apr 2013 09:24:33 CEST
#:Autore:    Lele Gaifax <lele@metapensiero.it>
#:Licenza:   GNU General Public License version 3 or later
#

from pyramid.i18n import TranslationStringFactory
from pyramid.events import NewRequest, subscriber


DOMAIN = 'sol-server'
"The translation domain of the server side"

translatable_string = TranslationStringFactory(DOMAIN)
"A function to make a translatable string."


available_languages = []

@subscriber(NewRequest)
def setAcceptedLanguagesLocale(event, _available_languages=available_languages):
    """Recognize the user preferred language.

    :param event: a Pyramid event
    :param _available_languages: the list of available languages (this is used
                                 as a cache, computed at the first call to this
                                 function)

    This function is automatically executed at each new request, and
    sets the ``_LOCALE_`` attribute of the request itself.
    """

    if not _available_languages:
        from pyramid.threadlocal import get_current_registry
        settings = get_current_registry().settings
        codes = settings.get('available_languages', 'en')
        # Put "en_US" before "en", otherwise the best_match()
        # mechanism does not work as expected
        _available_languages.extend(reversed(sorted(codes.split())))

    ui_language = event.request.session.get('ui_language')
    if ui_language and ui_language in _available_languages:
        event.request._LOCALE_ = ui_language
    else:
        if not event.request.accept_language:
            return

        accepted = event.request.accept_language
        event.request._LOCALE_ = accepted.best_match(_available_languages, 'en')


def translator(request):
    """Return a function that translates a given string in the specified request

    :param request: either None or a Pyramid request instance

    This is an helper function that handle the case when the request
    does not exist, for example while testing::

      >>> t = translator(None)
      >>> t('$first $last', mapping=dict(first='Foo', last='Bar'))
      'Foo Bar'
    """

    if request is not None:
        def wrapper(*args, **kw):
            if 'domain' not in kw:
                kw['domain'] = DOMAIN
            return request.localizer.translate(*args, **kw)
        return wrapper
    else:
        from string import Template
        return lambda s, **kw: Template(s).substitute(**kw.get('mapping', {}))


def gettext(s, **kw):
    """Immediately translate the given string with current request locale

    :param s: either a string or a TranslationString instance
    :keyword just_subst: by default False, True to disable the actual translation
                         and perform only mapping substitution
    """

    from string import Template
    from pyramid.threadlocal import get_current_request

    if 'domain' not in kw:
        kw['domain'] = DOMAIN

    text = None
    if not kw.pop('just_subst', False):
        request = get_current_request()
        if request is not None:
            text = request.localizer.translate(s, **kw)

    return text or Template(s).substitute(**kw.get('mapping', {}))


def ngettext(s, p, n, **kw):
    """Immediately translate the singular or plural form with current request locale

    :param s: either a string or a TranslationString instance with the
              singular form
    :param p: either a string or a TranslationString instance with the
              plural form
    :param n: an integer
    """

    from string import Template
    from pyramid.threadlocal import get_current_request

    if 'domain' not in kw:
        kw['domain'] = DOMAIN

    request = get_current_request()
    if request is not None:
        return request.localizer.pluralize(s, p, n, **kw)
    else:
        return Template(s if n==1 else p).substitute(**kw.get('mapping', {}))
