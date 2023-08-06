import unittest
from zope.component.testing import PlacelessSetup
from euphorie.deployment.tests.functional import EuphorieFunctionalTestCase
from Products.Five.testbrowser import Browser


class ViewTests(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        from zope.component import provideAdapter
        from zope.annotation.attribute import AttributeAnnotations
        from plone.folder.default import DefaultOrdering
        provideAdapter(AttributeAnnotations)
        provideAdapter(DefaultOrdering)

    def View(self, *a, **kw):
        from euphorie.client.api.country import View
        return View(*a, **kw)

    def test_plain_view(self):
        from zope.publisher.browser import TestRequest
        from euphorie.client.country import ClientCountry
        country = ClientCountry(id='nl', title=u'The Netherlands',
                country_type='eu-member')
        response = self.View(country, TestRequest()).do_GET()
        self.assertTrue(isinstance(response, dict))
        self.assertEqual(
                set(response),
                set(['id', 'title', 'type', 'sectors']))
        self.assertEqual(response['id'], 'nl')
        self.assertEqual(response['title'], u'The Netherlands')
        self.assertEqual(response['type'], 'eu-member')
        self.assertEqual(response['sectors'], [])

    def test_standard_session_info(self):
        from zope.publisher.browser import TestRequest
        from euphorie.client.country import ClientCountry
        from euphorie.client.sector import ClientSector
        country = ClientCountry(id='nl', title=u'The Netherlands',
                country_type='eu-member')
        country['ict'] = ClientSector(id='ict', title=u'ICT')
        response = self.View(country, TestRequest()).do_GET()
        self.assertEqual(len(response['sectors']), 1)
        sector_info = response['sectors'][0]
        self.assertTrue(isinstance(sector_info, dict))
        self.assertEqual(set(sector_info), set(['id', 'title']))
        self.assertEqual(sector_info['id'], 'ict')
        self.assertEqual(sector_info['title'], 'ICT')

    def test_detailed_session_info(self):
        import mock
        from zope.publisher.browser import TestRequest
        from euphorie.client.country import ClientCountry
        from euphorie.client.sector import ClientSector
        country = ClientCountry(id='nl', title=u'The Netherlands',
                country_type='eu-member')
        country['ict'] = ClientSector(id='ict', title=u'ICT')
        request = TestRequest()
        request.form['details'] = ''
        with mock.patch('euphorie.client.api.sector.View.do_GET') \
                as mock_sector_view:
            mock_sector_view.return_value = 'sector-detailed-info'
            response = self.View(country, request).do_GET()
            self.assertEqual(response['sectors'], ['sector-detailed-info'])

    def test_ignore_non_sector_child(self):
        from euphorie.ghost import PathGhost
        from zope.publisher.browser import TestRequest
        from euphorie.client.country import ClientCountry
        country = ClientCountry(id='nl', title=u'The Netherlands',
                country_type='eu-member')
        country['ict'] = PathGhost('ict')
        response = self.View(country, TestRequest()).do_GET()
        self.assertEqual(response['sectors'], [])


class BrowserTests(EuphorieFunctionalTestCase):
    def test_get(self):
        import json
        from euphorie.content.tests.utils import BASIC_SURVEY
        from euphorie.client.tests.utils import addSurvey
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = Browser()
        browser.open('http://nohost/plone/client/api/surveys/nl')
        response = json.loads(browser.contents)
        self.assertEqual(response['id'], 'nl')
