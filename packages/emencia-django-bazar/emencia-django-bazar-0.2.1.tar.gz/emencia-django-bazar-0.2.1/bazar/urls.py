# -*- coding: utf-8 -*-
"""
Bazar URLs
"""
from django.conf.urls import *

from bazar.views import IndexView
from bazar.views.entity import EntityIndexView, KindEntityIndexView, EntityDetailView, EntityEditView
from bazar.views.note import NoteCreateView, NoteDetailView, NoteEditView, TagNoteListView, NoteDeleteView

urlpatterns = patterns('',
    url(r'^$', IndexView.as_view(), name="index"),
    
    url(r'^entity/$', EntityIndexView.as_view(), name="entity-index"),
    
    url(r'^entity/(?P<kind>[-\w]+)/$', KindEntityIndexView.as_view(), name="entity-for-kind-index"),
    
    url(r'^entity/(?P<kind>[-\w]+)/(?P<entity_id>\d+)/$', EntityDetailView.as_view(), name="entity-detail"),
    url(r'^entity/(?P<kind>[-\w]+)/(?P<entity_id>\d+)/edit/$', EntityEditView.as_view(), name="entity-edit"),
    
    url(r'^entity/(?P<kind>[-\w]+)/(?P<entity_id>\d+)/note/create/$', NoteCreateView.as_view(), name="entity-note-create"),
    url(r'^entity/(?P<kind>[-\w]+)/(?P<entity_id>\d+)/(?P<note_id>\d+)/$', NoteDetailView.as_view(), name="entity-note-detail"),
    url(r'^entity/(?P<kind>[-\w]+)/(?P<entity_id>\d+)/(?P<note_id>\d+)/edit/$', NoteEditView.as_view(), name="entity-note-edit"),
    url(r'^entity/(?P<kind>[-\w]+)/(?P<entity_id>\d+)/(?P<note_id>\d+)/delete/$', NoteDeleteView.as_view(), name="entity-note-delete"),
    
    url(r'^tag/(?P<tag>[-\w]+)/$', TagNoteListView.as_view(), name="tag-note-list"),
)
