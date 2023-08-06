from Products.CMFPlone.utils import safe_unicode
from collective.address import messageFactory as _
from collective.address.vocabulary import get_pycountry_name
from plone.autoform.interfaces import IFormFieldProvider
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema
from zope.interface import alsoProvides


class IAddressable(model.Schema):
    """Abstract marker interface / schema class.
    """


class IAddress(IAddressable):
    """Address schema.
    """
    street = schema.TextLine(
        title=_(u'label_street', default=u'Street'),
        description=_(u'help_street', default=u''),
        required=False
    )
    zip_code = schema.TextLine(
        title=_(u'label_zip_code', default=u'Zip Code'),
        description=_(u'help_zip_code', default=u''),
        required=False
    )
    city = schema.TextLine(
        title=_(u'label_city', default=u'City'),
        description=_(u'help_city', default=u''),
        required=False
    )
    country = schema.Choice(
        title=_(u'label_country', default=u'Country'),
        description=_(u'help_country',
                      default=u'Select the country from the list.'),
        required=False,
        vocabulary='collective.address.CountryVocabulary'
    )


class IContact(IAddressable):
    """Contact schema.
    """
    email = schema.TextLine(
        title=_(u'label_email', default=u'Email'),
        description=_(u'help_email', default=u''),
        required=False
    )
    website = schema.TextLine(
        title=_(u'label_website', default=u'Website'),
        description=_(u'help_website', default=u''),
        required=False
    )
    phone = schema.TextLine(
        title=_(u'label_phone', default=u'Phone'),
        description=_(u'help_phone', default=u''),
        required=False
    )
    mobile = schema.TextLine(
        title=_(u'label_mobile', default=u'Mobile'),
        description=_(u'help_mobile', default=u''),
        required=False
    )
    fax = schema.TextLine(
        title=_(u'label_fax', default=u'Fax'),
        description=_(u'help_fax', default=u''),
        required=False
    )


class IPerson(IAddressable):
    """Person schema.
    """
    first_name = schema.TextLine(
        title=_(u'label_first_name', default=u'First Name'),
        description=_(u'help_first_name', default=u''),
        required=False
    )
    last_name = schema.TextLine(
        title=_(u'label_last_name', default=u'Last Name'),
        description=_(u'help_last_name', default=u''),
        required=False
    )
    academic_title = schema.TextLine(
        title=_(u'label_academic_titel', default=u'Academic title'),
        description=_(u'help_academic_title', default=u''),
        required=False
    )

    # Mark these interfaces as form field providers
alsoProvides(IAddress, IFormFieldProvider)
alsoProvides(IContact, IFormFieldProvider)
alsoProvides(IPerson, IFormFieldProvider)


# Text indexing
@indexer(IAddressable)
def searchable_text_indexer(obj):
    text = u''
    acc = IAddress(obj, None)
    if acc:
        text = u'{0}{1}{2}{3}{4}'.format(
            text,
            safe_unicode(acc.street) or '',
            safe_unicode(acc.zip_code) or '',
            safe_unicode(acc.city) or '',
            safe_unicode(get_pycountry_name(acc.country)) if acc.country else ''  # noqa
        )
    acc = IContact(obj, None)
    if acc:
        text = u'{0}{1}{2}{3}{4}{5}'.format(
            text,
            safe_unicode(acc.email) or '',
            safe_unicode(acc.website) or '',
            safe_unicode(acc.phone) or '',
            safe_unicode(acc.mobile) or '',
            safe_unicode(acc.fax) or '',
        )
    acc = IPerson(obj, None)
    if acc:
        text = u'{0}{1}{2}{3}'.format(
            text,
            safe_unicode(acc.first_name) or '',
            safe_unicode(acc.last_name) or '',
            safe_unicode(acc.academic_title) or '',
        )
    return text.strip()
