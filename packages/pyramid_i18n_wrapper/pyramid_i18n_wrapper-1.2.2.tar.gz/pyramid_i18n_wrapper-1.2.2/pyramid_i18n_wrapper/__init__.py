import pkg_resources

__version__ = pkg_resources.get_distribution('pyramid_i18n_wrapper').version

class LazyTranslationString:
    
    def __init__(self, translation_string_domain=None, request=None):
        from pyramid.i18n import TranslationStringFactory
        self.tsd = translation_string_domain
        self.tsf = TranslationStringFactory(translation_string_domain)
        self.request = request

    def translate(self, tstring, domain=None, mapping=None):
        localizer, domain = self._get_translate_obj(domain)
        return localizer.translate(self.tsf(tstring), domain, mapping)

    def pluralize(self, singular, plural, n, domain=None, mapping=None):
        localizer, domain = self._get_translate_obj(domain)
        return localizer.pluralize(
            self.tsf(singular), self.tsf(plural), n, domain, mapping)
    
    def _get_translate_obj(self, domain):
        if self.request is None:
            from pyramid.threadlocal import get_current_request
            request = get_current_request()
        else:
            request = self.request

        if domain is None:
            domain = self.tsd
        
        return request.localizer, domain
