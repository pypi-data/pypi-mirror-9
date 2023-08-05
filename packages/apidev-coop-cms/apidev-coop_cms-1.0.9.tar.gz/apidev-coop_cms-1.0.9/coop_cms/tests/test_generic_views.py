# -*- coding: utf-8 -*-

from django.conf import settings
if 'localeurl' in settings.INSTALLED_APPS:
    from localeurl.models import patch_reverse
    patch_reverse()

from django.utils.unittest import SkipTest

from coop_cms.apps.test_app.tests import GenericViewTestCase as BaseGenericViewTestCase


class GenericViewTestCase(BaseGenericViewTestCase):
    warning = """
    Add this to your settings.py to enable this test:
    if len(sys.argv)>1 and 'test' == sys.argv[1]:
        INSTALLED_APPS = INSTALLED_APPS + ('coop_cms.apps.test_app',)
    """
    
    def setUp(self):
        super(GenericViewTestCase, self).setUp()
        if not ('coop_cms.apps.test_app' in settings.INSTALLED_APPS):
            print self.warning
            raise SkipTest()
