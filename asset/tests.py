"""
This module contains test cases for the assets application.
"""

from django.test import RequestFactory, TestCase
from django.urls import reverse, resolve
from asset.cbv.asset_category import AssetFormView
from horilla.horilla_middlewares import _thread_locals

class AssetFormViewTest(TestCase):
    def test_asset_form_view_attributes(self):
        """
        Test that AssetFormView removes the 'onchange' attribute from 'asset_lot_number_id'
        and adds 'dynamic_create' choice manually.
        """
        factory = RequestFactory()
        request = factory.get('/')

        class MockSession(dict):
            session_key = 'test_session_key'
        request.session = MockSession()

        # Mock user with permissions
        class MockUser:
            def has_perm(self, perm):
                return True
        request.user = MockUser()

        _thread_locals.request = request

        view = AssetFormView()
        view.request = request
        view.kwargs = {}

        try:
            form = view.get_form()
            field = form.fields.get('asset_lot_number_id')
            if field:
                attrs = field.widget.attrs

                # Check that 'batchNoChange' is NOT in 'onchange'
                if 'onchange' in attrs:
                    self.assertNotIn('batchNoChange', attrs['onchange'],
                                     "batchNoChange should be removed from onchange attribute in AssetFormView")

                # Check choices
                choices = getattr(field, 'choices', [])
                has_dynamic = any(c[0] == 'dynamic_create' for c in choices)
                self.assertTrue(has_dynamic, "'dynamic_create' choice should be present")

        except Exception as e:
            self.fail(f"AssetFormView.get_form raised exception: {e}")

    def test_dynamic_create_url(self):
        """
        Test that the static URL for dynamic batch creation resolves.
        """
        url = reverse('asset-batch-dynamic-create')
        match = resolve(url)
        self.assertIsNotNone(match)
