# -*- coding: utf-8 -*-
"""
Common views
"""
from django.conf import settings
from django.views import generic
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin

from bazar.models import Entity, Note
from bazar.forms.entity import EntityForm, EntityForKindForm
from bazar.utils.mixins import KindMixin, EntityMixin
from bazar.utils.views import ListAppendView


class EntityIndexView(LoginRequiredMixin, ListAppendView):
    """
    Entity Index view, all kind mixed
    """
    model = Entity
    form_class = EntityForm
    template_name = "bazar/entity/index.html"
    paginate_by = settings.BAZAR_ENTITY_INDEX_PAGINATE
    
    def annotate_notes(self, queryset):
        return queryset.annotate(num_notes=Count('note'))
    
    def get_queryset(self):
        return self.annotate_notes(super(EntityIndexView, self).get_queryset())

    def get_success_url(self):
        return reverse('bazar:entity-index')


class KindEntityIndexView(KindMixin, EntityIndexView):
    """
    Entity index view for a given kind
    """
    model = Entity
    form_class = EntityForKindForm
    template_name = "bazar/entity/index.html"
    paginate_by = settings.BAZAR_ENTITY_INDEX_PAGINATE
    
    def get_queryset(self):
        q = super(EntityIndexView, self).get_queryset()
        return self.annotate_notes(q.filter(kind=self.get_kind()))

    def get_form_kwargs(self):
        kwargs = super(KindEntityIndexView, self).get_form_kwargs()
        kwargs.update({'kind': self.get_kind()})
        return kwargs

    def get_success_url(self):
        return reverse('bazar:entity-for-kind-index', args=(self.get_kind(),))


class EntityDetailView(LoginRequiredMixin, EntityMixin, generic.DetailView):
    """
    Entity detail view
    """
    model = Entity
    template_name = "bazar/entity/detail.html"
    context_object_name = "entity_instance"
    
    def get_object(self, queryset=None):
        return self.get_entity()
    
    def get_notes(self):
        return self.object.note_set.all().order_by('-created')
    

class EntityEditView(LoginRequiredMixin, EntityMixin, generic.UpdateView):
    """
    Entity edit view
    """
    model = Entity
    form_class = EntityForm
    template_name = 'bazar/entity/form.html'
    context_object_name = "entity_instance"
    
    def get_object(self, queryset=None):
        return self.get_entity()

    def get_success_url(self):
        return self.object.get_absolute_url()
