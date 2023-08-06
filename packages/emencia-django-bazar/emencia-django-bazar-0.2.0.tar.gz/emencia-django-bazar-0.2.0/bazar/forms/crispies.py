"""
Crispy forms layouts
"""
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms_foundation.layout import Layout, Row, Column, ButtonHolderPanel, Submit

def entity_helper(form_tag=True, kind=None):
    """
    Entity form layout helper
    """
    helper = FormHelper()
    helper.form_action = '.'
    helper.attrs = {'data_abide': ''}
    helper.form_tag = form_tag
    
    fieldset = [
        Row(
            Column(
                'name',
                css_class='small-12'
            ),
        ),
    ]
    
    if kind is None:
        fieldset.append(
            Row(
                Column(
                    'kind',
                    css_class='small-12'
                ),
            ),
        )
    
    fieldset = fieldset+[
        Row(
            Column(
                'adress',
                css_class='small-12'
            ),
        ),
        Row(
            Column(
                'town',
                css_class='small-12 medium-8'
            ),
            Column(
                'zipcode',
                css_class='small-12 medium-4'
            ),
        ),
        Row(
            Column(
                'phone',
                css_class='small-12'
            ),
        ),
        ButtonHolderPanel(
            Submit('submit', _('Submit')),
            css_class='text-right',
        ),
    ]
    helper.layout = Layout(*fieldset)
    
    return helper


def note_helper(form_tag=True):
    """
    Note form layout helper
    """
    helper = FormHelper()
    helper.form_action = '.'
    helper.attrs = {'data_abide': ''}
    helper.form_tag = form_tag
    
    helper.layout = Layout(
        Row(
            Column(
                'title',
                css_class='small-12'
            ),
        ),
        Row(
            Column(
                'content',
                css_class='small-12'
            ),
        ),
        Row(
            Column(
                'tags',
                css_class='small-12'
            ),
        ),
        ButtonHolderPanel(
            Submit('submit', _('Submit')),
            css_class='text-right',
        ),
    )
    
    return helper


def note_delete_helper(form_tag=True):
    """
    Note delete form layout helper
    """
    helper = FormHelper()
    helper.form_action = '.'
    helper.attrs = {'data_abide': ''}
    helper.form_tag = form_tag
    
    helper.layout = Layout(
        ButtonHolderPanel(
            Row(
                Column(
                    'confirm',
                    css_class='small-12 medium-8'
                ),
                Column(
                    Submit('submit', _('Submit')),
                    css_class='small-12 medium-4 text-right'
                ),
            ),
        ),
    )
    
    return helper
