# -*- coding: utf-8 -*-
"""
Common views
"""
from django.conf import settings
from django.views import generic
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin

from taggit.models import Tag

from bazar.models import Entity, Note
from bazar.forms.note import NoteForm, NoteDeleteForm
from bazar.utils.mixins import MarkupMixin, EntityMixin


class NoteEntityBaseView(EntityMixin):
    """
    Base view to get the entity from note
    """
    def get_context_data(self, **kwargs):
        context = super(NoteEntityBaseView, self).get_context_data(**kwargs)
        context.update({
            'entity_instance': self.entity,
        })
        return context
    
    def get(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteEntityBaseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteEntityBaseView, self).post(request, *args, **kwargs)


class NoteCreateView(LoginRequiredMixin, MarkupMixin, NoteEntityBaseView, generic.CreateView):
    """
    Form view to create a note for an entity
    """
    model = Note
    template_name = "bazar/note/form.html"
    form_class = NoteForm

    def get_success_url(self):
        return reverse('bazar:entity-detail', args=[self.get_kind(), self.entity.id])

    def get_form_kwargs(self):
        kwargs = super(NoteCreateView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
            'entity': self.entity,
        })
        return kwargs


class NoteEditView(LoginRequiredMixin, MarkupMixin, NoteEntityBaseView, generic.UpdateView):
    """
    Form view to edit a note for an entity
    """
    model = Note
    template_name = "bazar/note/form.html"
    form_class = NoteForm
    
    def get_object(self, queryset=None):
        return get_object_or_404(Note, entity=self.get_entity_id(), pk=self.kwargs['note_id'])

    def get_success_url(self):
        return reverse('bazar:entity-note-detail', args=[self.get_kind(), self.entity.id, self.object.id])

    def get_context_data(self, **kwargs):
        context = super(NoteEditView, self).get_context_data(**kwargs)
        context.update({
            'note_instance': self.object,
        })
        return context
    
    def get_form_kwargs(self):
        kwargs = super(NoteEditView, self).get_form_kwargs()
        kwargs.update({
            'author': self.request.user,
            'entity': self.entity,
        })
        return kwargs


class TagNoteListView(LoginRequiredMixin, generic.ListView):
    """
    List notes from a tag
    """
    model = Note
    template_name = "bazar/note/list.html"
    paginate_by = settings.BAZAR_NOTE_INDEX_PAGINATE
    
    def get_tags_slug(self):
        """
        Tag slug comes from url kwargs
        """
        return self.kwargs['tag']
    
    def get_tag(self):
        """
        Getting Tag object
        """
        return get_object_or_404(Tag, slug=self.get_tags_slug())
    
    def get_queryset(self):
        return self.model.objects.select_related('entity').filter(tags__slug__in=[self.get_tags_slug()])

    def get(self, request, *args, **kwargs):
        self.tag = self.get_tag()
        return super(TagNoteListView, self).get(request, *args, **kwargs)


class NoteDetailView(LoginRequiredMixin, MarkupMixin, NoteEntityBaseView, generic.DetailView):
    """
    Note detail view
    """
    model = Entity
    template_name = "bazar/note/detail.html"
    context_object_name = "note_instance"
    
    def get_object(self, queryset=None):
        return get_object_or_404(Note, entity=self.get_entity_id(), pk=self.kwargs['note_id'])


class NoteDeleteView(LoginRequiredMixin, NoteEntityBaseView, generic.UpdateView):
    """
    Note delete view
    """
    model = Note
    form_class = NoteDeleteForm
    template_name = 'bazar/note/delete_form.html'
    
    def get_object(self, queryset=None):
        return get_object_or_404(Note, entity=self.get_entity_id(), pk=self.kwargs['note_id'])

    def get_context_data(self, **kwargs):
        context = super(NoteDeleteView, self).get_context_data(**kwargs)
        context.update({
            'note_instance': self.object,
        })
        return context

    def get_success_url(self):
        return reverse('bazar:entity-detail', args=[self.get_kind(), self.entity.id])
    
    def get(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteDeleteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.entity = self.get_entity()
        return super(NoteDeleteView, self).post(request, *args, **kwargs)
