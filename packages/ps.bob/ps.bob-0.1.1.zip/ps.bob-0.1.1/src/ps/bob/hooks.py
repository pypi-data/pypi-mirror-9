# -*- coding: utf-8 -*-
"""Pre- and Post-Render Hooks for mr.bob."""

# python imports
from mrbob.bobexceptions import (
    ConfigurationError,
    SkipQuestion,
)


def prepare_diazo_render(configurator):
    """Some variables to make templating easier."""

    theme_type = configurator.variables['theme.type']
    if theme_type == 'core':
        namespace = 'ps'
        namespace2 = 'diazo'
    elif theme_type == 'customer':
        namespace = 'customer'
        namespace2 = 'diazo'
    else:
        raise ConfigurationError('The theme type was not defined.')

    dottedname = '.'.join([
        namespace,
        namespace2,
        configurator.variables['package.name'],
    ])
    configurator.variables['package.dottedname'] = dottedname
    configurator.variables['package.namespace'] = namespace
    configurator.variables['package.namespace2'] = namespace2

    # package.uppercasename = 'PS_DIAZO_MYTHEME'
    configurator.variables['package.uppercasename'] = \
        dottedname.replace('.', '_').upper()

    camelcasename = dottedname.replace('.', ' ').title()\
        .replace(' ', '')\
        .replace('_', '')
    testlayer = '{0}Layer'.format(camelcasename)

    # package.testlayer = 'PsDiazoMythemeLayer'
    configurator.variables['package.testlayer'] = testlayer

    browserlayer = 'I{0}'.format(testlayer)
    # package.browserlayer = 'IPsDiazoMythemeLayer'
    configurator.variables['package.browserlayer'] = browserlayer

    # package.longname = 'psdiazomytheme'
    configurator.variables['package.longname'] = camelcasename.lower()


def diazo_theme_customer_only(configurator, question):
    """Allow question only when theme type is 'customer'."""
    theme_type = configurator.variables['theme.type']
    if theme_type == 'core':
        raise SkipQuestion


def diazo_theme_with_base_only(configurator, question):
    """Allow question only when theme should be extended."""
    theme_base = configurator.variables.get('theme.base')
    if not theme_base:
        raise SkipQuestion
