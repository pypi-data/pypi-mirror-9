from pycountry import ExistingCountries as BaseExistingCountries, currencies, languages, DATABASE_DIR
from frasco.utils import slugify
import os


__all__ = ('countries', 'currencies', 'languages')


class ExistingCountries(BaseExistingCountries):
    """Country database with an additional slug field
    """
    generated_fields = dict(slug=lambda x: slugify(x.name))


countries = ExistingCountries(os.path.join(DATABASE_DIR, 'iso3166.xml'))