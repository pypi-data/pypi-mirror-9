def wtforms_translation_string_factory(domain):
    '''Let wtforms has lazy translation facility.'''
    
    class _WTFormsLazyTranslationString:
        '''This class used for deferring message translation until rendering stage.'''

        def __init__(self, msg, mapping=None):
            from . import LazyTranslationString
            self.msg = msg
            self.mapping = mapping
            self.lts = LazyTranslationString(domain)

        def __str__(self):
            return self.lts.translate(self.msg, mapping=self.mapping)

        def __mod__(self, data):
            return self.__str__() % data

        def format(self, *args, **kargs):
            return self.__str__().format(*args, **kargs)
    
    return _WTFormsLazyTranslationString


def wtforms_translate_i18n_now(form):
    '''
    When using wtforms_translation_string_factory with json renderer, we need translate strings
    first in order to render the result to the front. This function helps us to achieve this purpose.
    '''
    from wtforms import FormField, FieldList
    for key, field in form._fields.items():
        if isinstance(field, FormField):
            wtforms_translate_i18n_now(field)
        elif isinstance(field, FieldList):
            for entry in field.entries:
                _translate_field_now(entry)
        else:
            _translate_field_now(field)

def _translate_field_now(field):
    field.label.text = str(field.label.text)
    field.errors = [ str(i) for i in field.errors ]
