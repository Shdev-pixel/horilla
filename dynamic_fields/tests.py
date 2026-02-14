from django.test import TestCase, RequestFactory
from django import forms
from dynamic_fields.models import DynamicField
from dynamic_fields.forms import DynamicFieldForm
from base.models import WorkType
from horilla.horilla_middlewares import _thread_locals

class DynamicFieldsTest(TestCase):
    def setUp(self):
        # Create a dynamic field for WorkType
        self.df = DynamicField.objects.create(
            model="base.models.WorkType",
            verbose_name="Test Dynamic Field",
            type="1", # CharField
            is_required=False
        )

    def test_dynamic_field_in_form(self):
        """
        Test that the dynamic field appears in the model form.
        And ensure it doesn't crash if request is missing in _thread_locals.
        """

        # Ensure _thread_locals.request is not set (or cleared)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request

        class WorkTypeForm(forms.ModelForm):
            class Meta:
                model = WorkType
                fields = "__all__"

        form = WorkTypeForm()
        self.assertIn(self.df.field_name, form.fields)
        self.assertIsInstance(form.fields[self.df.field_name].widget, forms.Widget)

    def test_dynamic_field_with_request(self):
        """
        Test that it works when request IS present.
        """
        factory = RequestFactory()
        request = factory.get('/')
        request.user = type('User', (object,), {'has_perm': lambda self, perm: True})()

        _thread_locals.request = request

        class WorkTypeForm(forms.ModelForm):
            class Meta:
                model = WorkType
                fields = "__all__"

        form = WorkTypeForm()
        self.assertIn(self.df.field_name, form.fields)
        self.assertIn('add_df', form.fields) # Should be present due to permissions

    def tearDown(self):
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
