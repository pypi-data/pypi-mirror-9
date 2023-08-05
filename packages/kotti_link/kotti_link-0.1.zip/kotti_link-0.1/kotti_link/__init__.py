from pyramid.i18n import TranslationStringFactory

_ = TranslationStringFactory('kotti_link')


def kotti_configure(settings):

    settings['pyramid.includes'] += ' kotti_link'
    settings['kotti.available_types'] += ' kotti_link.resources.Link'


def includeme(config):

    config.add_translation_dirs('kotti_link:locale')
    config.scan(__name__)
