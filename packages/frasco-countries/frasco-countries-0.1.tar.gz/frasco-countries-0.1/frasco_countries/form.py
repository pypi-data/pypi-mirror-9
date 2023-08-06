from frasco import current_context, current_app
from wtforms import SelectField
from .db import *
from . import current_country, country_currency


class CountryField(SelectField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', [(c.alpha2, c.name) for c in countries])
        if current_country:
            kwargs.setdefault("default", current_country.alpha2)
        super(CountryField, self).__init__(*args, **kwargs)


class LanguageField(SelectField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', [(c.alpha2, c.name) for c in languages if hasattr(c, "alpha2")])
        kwargs.setdefault("default", "en")
        super(LanguageField, self).__init__(*args, **kwargs)


class CurrencyField(SelectField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', [(c.letter, c.name) for c in currencies])
        try:
            if current_country:
                kwargs.setdefault('default', country_currency(current_country))
        except:
            pass
        super(CurrencyField, self).__init__(*args, **kwargs)
