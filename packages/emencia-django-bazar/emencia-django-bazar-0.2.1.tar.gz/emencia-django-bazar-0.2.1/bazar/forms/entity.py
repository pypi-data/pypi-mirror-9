# -*- coding: utf-8 -*-
"""
Category forms
"""
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from bazar.forms import CrispyFormMixin
from bazar.utils.imports import safe_import_module
from bazar.models import Entity

class EntityForm(CrispyFormMixin, forms.ModelForm):
    """
    Category form
    """
    crispy_form_helper_path = 'bazar.forms.crispies.entity_helper'
    
    def __init__(self, *args, **kwargs):
        super(EntityForm, self).__init__(*args, **kwargs)
        super(forms.ModelForm, self).__init__(*args, **kwargs)
    
    class Meta:
        model = Entity

class EntityForKindForm(EntityForm):
    """
    Category form
    """
    crispy_form_helper_path = 'bazar.forms.crispies.entity_helper'
    
    def __init__(self, *args, **kwargs):
        self.kind = kwargs.pop('kind', None)
        
        self.crispy_form_helper_kwargs = {
            'kind': self.kind,
        }
        
        super(EntityForKindForm, self).__init__(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        instance = super(EntityForKindForm, self).save(commit=False, *args, **kwargs)
        instance.kind = self.kind
        instance.save()
        
        return instance
    
    class Meta:
        model = Entity
        fields = ('name', 'adress', 'town', 'zipcode', 'phone')
