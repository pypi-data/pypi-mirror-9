collective.address
==================

This package provides an Dexterity behavior for location addresses to be used
in Dexterity based types.


How to provide a default value for the country field
----------------------------------------------------

If you want to provide a default value for the IAddress' country field, you can
provide an ComputedWidgetAttribute adapter like so::

    from zope.component import provideAdapter
    from z3c.form.widget import ComputedWidgetAttribute
    from collective.address.behaviors import IAddress
    DEFAULT_COUNTRY = "040"  # Austria
    provideAdapter(ComputedWidgetAttribute(
        lambda data: DEFAULT_COUNTRY,
        field=IAddress['country']), name='default')
