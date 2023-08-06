# -*- coding: utf-8 -*-
"""
Common mixins
"""
from django.conf import settings
from django.shortcuts import get_object_or_404

from bazar.models import Entity


class MarkupMixin(object):
    """
    Mixin to contains conditional markup stuff
    """
    def get_context_data(self, **kwargs):
        context = super(MarkupMixin, self).get_context_data(**kwargs)
        context.update({
            'BAZAR_MARKUP_FIELD_HELPER_PATH': settings.BAZAR_MARKUP_FIELD_HELPER_PATH,
            'BAZAR_MARKUP_FIELD_JS_TEMPLATE': settings.BAZAR_MARKUP_FIELD_JS_TEMPLATE,
            'BAZAR_MARKUP_VALIDATOR_HELPER_PATH': settings.BAZAR_MARKUP_VALIDATOR_HELPER_PATH,
            'BAZAR_MARKUP_RENDER_TEMPLATE': settings.BAZAR_MARKUP_RENDER_TEMPLATE,
        })
        return context


class KindMixin(object):
    """
    Just a simple mixin to share helper to get the kind display
    """
    def get_kind(self):
        """
        Default kind value come from url kwargs
        """
        return self.kwargs['kind']
    
    def get_kind_display(self):
        return dict(settings.ENTITY_KINDS).get(self.get_kind())


class EntityMixin(KindMixin):
    """
    A mixin to get an entity instance
    """
    def get_entity_id(self):
        return self.kwargs['entity_id']
    
    def get_entity(self):
        return get_object_or_404(Entity, kind=self.get_kind(), pk=self.get_entity_id())
