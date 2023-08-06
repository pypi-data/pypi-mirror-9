# -*- coding: utf-8 -*-
"""Tests for ps.bob templates."""

# python imports
from scripttest import TestFileEnvironment
import os
import shutil
import tempfile
import unittest2 as unittest


class BaseTemplateTest(unittest.TestCase):
    """Base class for all ps.bob test cases."""

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tempdir)

        # docs http://pythonpaste.org/scripttest/
        self.env = TestFileEnvironment(
            os.path.join(self.tempdir, 'test-output'),
            ignore_hidden=False,
        )

    def create_template(self):
        """Run mr.bob to create your template."""
        options = {
            'dir': os.path.join(os.path.dirname(__file__)),
            'template': self.template,
            'answers_file': self.answers_file,
        }
        return self.env.run(
            '{dir}/bin/mrbob --config '
            '{dir}/{answers_file} {dir}/src/ps/bob/{template}'.format(
                **options
            )
        )


class DiazoThemeTest(BaseTemplateTest):
    """Test case for the `diazo_theme` template."""
    template = 'diazo_theme'

    def test_core_template(self):
        """Validate the `diazo_theme` template.

        Generate a project from a template, test which files were created
        and run all tests in the generated package.
        """
        self.maxDiff = None
        self.answers_file = 'test_answers/diazo_theme_core.ini'
        result = self.create_template()
        p = 'ps.diazo.mytheme'
        p_src = p + '/src/ps/diazo'
        expected = [
            p,
            p + '/.csslintrc',
            p + '/.editorconfig',
            p + '/.gitignore',
            p + '/.jshintignore',
            p + '/.travis.yml',
            p + '/CHANGES.rst',
            p + '/README.rst',
            p + '/bootstrap.py',
            p + '/buildout.cfg',
            p + '/docs',
            p + '/docs/README',
            p + '/docs/_images',
            p + '/docs/_images/README',
            p + '/docs/source',
            p + '/docs/source/_static',
            p + '/docs/source/_static/logo.png',
            p + '/docs/source/_templates',
            p + '/docs/source/_templates/empty',
            p + '/docs/source/conf.py',
            p + '/docs/source/configuration.rst',
            p + '/docs/source/index.rst',
            p + '/setup.cfg',
            p + '/setup.py',
            p + '/src',
            p + '/src/ps',
            p + '/src/ps/__init__.py',
            p_src,
            p_src + '/__init__.py',
            p_src + '/mytheme',
            p_src + '/mytheme/Extensions',
            p_src + '/mytheme/Extensions/install.py',
            p_src + '/mytheme/__init__.py',
            p_src + '/mytheme/config.py',
            p_src + '/mytheme/configure.zcml',
            p_src + '/mytheme/diazo_resources',
            p_src + '/mytheme/diazo_resources/favicon.ico',
            p_src + '/mytheme/diazo_resources/index.html',
            p_src + '/mytheme/diazo_resources/manifest.cfg',
            p_src + '/mytheme/diazo_resources/preview.png',
            p_src + '/mytheme/diazo_resources/rules.xml',
            p_src + '/mytheme/diazo_resources/static',
            p_src + '/mytheme/diazo_resources/static/main.css',
            p_src + '/mytheme/diazo_resources/static/main.js',
            p_src + '/mytheme/interfaces.py',
            p_src + '/mytheme/locales',
            p_src + '/mytheme/locales/en',
            p_src + '/mytheme/locales/en/LC_MESSAGES',
            p_src + '/mytheme/locales/en/LC_MESSAGES/ps.diazo.mytheme.po',
            p_src + '/mytheme/locales/manual.pot',
            p_src + '/mytheme/locales/plone.pot',
            p_src + '/mytheme/locales/ps.diazo.mytheme.pot',
            p_src + '/mytheme/migration.py',
            p_src + '/mytheme/profiles',
            p_src + '/mytheme/profiles.zcml',
            p_src + '/mytheme/profiles/default',
            p_src + '/mytheme/profiles/default/browserlayer.xml',
            p_src + '/mytheme/profiles/default/cssregistry.xml',
            p_src + '/mytheme/profiles/default/jsregistry.xml',
            p_src + '/mytheme/profiles/default/metadata.xml',
            p_src + '/mytheme/profiles/default/psdiazomytheme_marker.txt',
            p_src + '/mytheme/profiles/default/theme.xml',
            p_src + '/mytheme/profiles/uninstall',
            p_src + '/mytheme/profiles/uninstall/browserlayer.xml',
            p_src + '/mytheme/profiles/uninstall/theme.xml',
            p_src + '/mytheme/setuphandlers.py',
            p_src + '/mytheme/template_overrides',
            p_src + '/mytheme/template_overrides/README',
            p_src + '/mytheme/testing.py',
            p_src + '/mytheme/tests',
            p_src + '/mytheme/tests/__init__.py',
            p_src + '/mytheme/tests/robot',
            p_src + '/mytheme/tests/robot/keywords.robot',
            p_src + '/mytheme/tests/robot/test_setup.robot',
            p_src + '/mytheme/tests/test_robot.py',
            p_src + '/mytheme/tests/test_setup.py',
            p + '/travis.cfg',
        ]
        self.assertItemsEqual(result.files_created.keys(), expected)

    def test_customer_template(self):
        """Validate the `diazo_theme` template.

        Generate a project from a template, test which files were created
        and run all tests in the generated package.
        """
        self.maxDiff = None
        self.answers_file = 'test_answers/diazo_theme_customer.ini'
        result = self.create_template()
        p = 'customer.diazo.domain'
        p_src = p + '/src/customer/diazo'
        expected = [
            p,
            p + '/.csslintrc',
            p + '/.editorconfig',
            p + '/.gitignore',
            p + '/.jshintignore',
            p + '/.travis.yml',
            p + '/CHANGES.rst',
            p + '/README.rst',
            p + '/bootstrap.py',
            p + '/buildout.cfg',
            p + '/docs',
            p + '/docs/README',
            p + '/docs/_images',
            p + '/docs/_images/README',
            p + '/docs/source',
            p + '/docs/source/_static',
            p + '/docs/source/_static/logo.png',
            p + '/docs/source/_templates',
            p + '/docs/source/_templates/empty',
            p + '/docs/source/conf.py',
            p + '/docs/source/configuration.rst',
            p + '/docs/source/index.rst',
            p + '/setup.cfg',
            p + '/setup.py',
            p + '/src',
            p + '/src/customer',
            p + '/src/customer/__init__.py',
            p_src,
            p_src + '/__init__.py',
            p_src + '/domain',
            p_src + '/domain/Extensions',
            p_src + '/domain/Extensions/install.py',
            p_src + '/domain/__init__.py',
            p_src + '/domain/config.py',
            p_src + '/domain/configure.zcml',
            p_src + '/domain/diazo_resources',
            p_src + '/domain/diazo_resources/favicon.ico',
            p_src + '/domain/diazo_resources/index.html',
            p_src + '/domain/diazo_resources/manifest.cfg',
            p_src + '/domain/diazo_resources/preview.png',
            p_src + '/domain/diazo_resources/rules.xml',
            p_src + '/domain/diazo_resources/static',
            p_src + '/domain/diazo_resources/static/main.css',
            p_src + '/domain/diazo_resources/static/main.js',
            p_src + '/domain/interfaces.py',
            p_src + '/domain/locales',
            p_src + '/domain/locales/en',
            p_src + '/domain/locales/en/LC_MESSAGES',
            p_src + '/domain/locales/en/LC_MESSAGES/customer.diazo.domain.po',
            p_src + '/domain/locales/manual.pot',
            p_src + '/domain/locales/plone.pot',
            p_src + '/domain/locales/customer.diazo.domain.pot',
            p_src + '/domain/migration.py',
            p_src + '/domain/profiles',
            p_src + '/domain/profiles.zcml',
            p_src + '/domain/profiles/default',
            p_src + '/domain/profiles/default/browserlayer.xml',
            p_src + '/domain/profiles/default/cssregistry.xml',
            p_src + '/domain/profiles/default/jsregistry.xml',
            p_src + '/domain/profiles/default/metadata.xml',
            p_src + '/domain/profiles/default/customerdiazodomain_marker.txt',
            p_src + '/domain/profiles/default/theme.xml',
            p_src + '/domain/profiles/uninstall',
            p_src + '/domain/profiles/uninstall/browserlayer.xml',
            p_src + '/domain/profiles/uninstall/theme.xml',
            p_src + '/domain/setuphandlers.py',
            p_src + '/domain/template_overrides',
            p_src + '/domain/template_overrides/README',
            p_src + '/domain/testing.py',
            p_src + '/domain/tests',
            p_src + '/domain/tests/__init__.py',
            p_src + '/domain/tests/robot',
            p_src + '/domain/tests/robot/keywords.robot',
            p_src + '/domain/tests/robot/test_setup.robot',
            p_src + '/domain/tests/test_robot.py',
            p_src + '/domain/tests/test_setup.py',
            p + '/travis.cfg',
        ]
        self.assertItemsEqual(result.files_created.keys(), expected)
