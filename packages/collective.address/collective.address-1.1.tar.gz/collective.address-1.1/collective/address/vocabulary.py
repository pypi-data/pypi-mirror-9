from zope.interface import directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
import pycountry
from Products.CMFPlone.utils import safe_unicode


def CountryVocabulary(context, query=None):
    """Vocabulary factory for countries regarding to ISO3166.
    """
    items = [SimpleTerm(value=it.numeric, title=safe_unicode(it.name))
             for it in pycountry.countries
             if query is None
             or safe_unicode(query.lower()) in safe_unicode(it.name.lower())]
    return SimpleVocabulary(items)
directlyProvides(CountryVocabulary, IVocabularyFactory)


def get_pycountry_name(country_id):
    if not country_id:
        return None
    country = pycountry.countries.get(numeric=country_id)
    return country.name
