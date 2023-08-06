from frasco import Feature, action, hook, OptionMissingError, current_context, session, g
import flask
from werkzeug.local import LocalProxy
from .db import *


def _get_current_country():
    """Returns the current set of assets in the request stack.
    """
    return getattr(flask._request_ctx_stack.top, 'current_country', None)


current_country = LocalProxy(_get_current_country)


def list_countries():
    """Returns a list of all available countries as country objects
    """
    return countries


def country_name(alpha2):
    """Returns the name of the country identified by the alpha2 code
    """
    try:
        return countries.get(alpha2=alpha2).name
    except:
        return None


# pycountry does not provide currency information for country in the Eurozone
eurozone_countries = ("040", "056", "196", "233", "246", "250", "276", "300", "372",
    "380", "428", "442", "470", "528", "620", "703", "705", "724")


def country_currency(alpha2_or_country_obj):
    """Returns the currency code of the specified country
    """
    if isinstance(alpha2_or_country_obj, (str, unicode)):
        country = countries.get(alpha2=alpha2_or_country_obj)
    else:
        country = alpha2_or_country_obj
    if country.numeric in eurozone_countries:
        return "EUR"
    try:
        c = currencies.get(numeric=country.numeric)
    except:
        return None
    return c.letter


class CountriesFeature(Feature):
    name = "countries"
    defaults = {"use_geolocation_as_default": True}

    def init_app(self, app):
        app.add_template_global(list_countries)
        app.add_template_global(country_name)
        app.add_template_global(country_currency)

    @hook()
    def before_request(self, *args, **kwargs):
        current_context["current_country"] = current_country
        if "current_country_code" not in session:
            if not self.options["use_geolocation_as_default"] or "geo_country_code" not in current_context.data:
                return
            alpha2 = current_context.data.geo_country_code
        else:
            alpha2 = session["current_country_code"]
        if alpha2:
            flask._request_ctx_stack.top.current_country = countries.get(alpha2=alpha2)

    @action("set_current_country", default_option="alpha2")
    def set_current(self, country=None, is_global=True, **kwargs):
        if not country:
            try:
                country = countries.get(**kwargs)
            except:
                pass
        if not country:
            raise OptionMissingError("No way to identify the current country")

        flask._request_ctx_stack.top.current_country = country
        if is_global:
            session["current_country_code"] = country.alpha2
        return country

    @action("get_country", default_option="alpha2", as_="country")
    def get(self, **kwargs):
        try:
            return countries.get(**kwargs)
        except:
            raise OptionMissingError("No way to identify the country")

    @action("geolocate_country", as_="country")
    def geolocate(self):
        return countries.get(alpha2=current_context.data.geo_country_code)

    @action(default_option="letter", as_="currency")
    def get_currency(self, **kwargs):
        try:
            return currencies.get(**kwargs)
        except:
            raise OptionMissingError("No way to identify the current currency")

    @action(default_option="alpha2", as_="language")
    def get_language(self, **kwargs):
        try:
            return languages.get(**kwargs)
        except:
            raise OptionMissingError("No way to identify the current language")


try:
    import frasco_forms.form
    import form
    frasco_forms.form.field_type_map.update({
        "country": form.CountryField,
        "language": form.LanguageField,
        "currency": form.CurrencyField})
except ImportError:
    pass