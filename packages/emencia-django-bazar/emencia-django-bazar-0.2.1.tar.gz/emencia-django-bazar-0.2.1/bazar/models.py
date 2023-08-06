# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now as tz_now

from localflavor.fr.forms import FRZipCodeField, FRPhoneNumberField

from taggit.managers import TaggableManager

class Entity(models.Model):
    """
    Entity
    
    Most of informations for notes are related to an entity, so it's best to 
    have them to improve data structures.
    """
    created = models.DateTimeField(_("created"), editable=False, null=True, blank=True)
    modified = models.DateTimeField(_("modified"), editable=False, null=True, blank=True)
    
    kind = models.CharField(_('kind'), choices=settings.ENTITY_KINDS, default=settings.DEFAULT_ENTITY_KIND, max_length=40, blank=False)
    
    name = models.CharField(_("name"), blank=False, max_length=255, unique=True)
    adress = models.TextField(_('full adress'), blank=True)
    phone = models.CharField(_('phone'), max_length=15, blank=True)
    # TODO: to remove
    town = models.CharField(_('town'), max_length=75, blank=True)
    zipcode = models.CharField(_('zipcode'), max_length=6, blank=True)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('bazar:entity-detail', [self.kind, self.id])

    def save(self, *args, **kwargs):
        """
        Fill 'created' and 'modified' attributes on first create
        """
        if self.created is None:
            self.created = tz_now()
        
        if self.modified is None:
            self.modified = self.created
            
        super(Entity, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")


class Note(models.Model):
    """
    Note
    """
    created = models.DateTimeField(_("created"), editable=False, null=True, blank=True)
    modified = models.DateTimeField(_("modified"), editable=False, null=True, blank=True)
    
    author = models.ForeignKey(User, verbose_name=_("author"))#, editable=False, blank=False)
    entity = models.ForeignKey(Entity, verbose_name=_("entity"), null=True, blank=True)
    
    title = models.CharField(_("title"), max_length=150)
    content = models.TextField(_('content'))
    
    tags = TaggableManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('bazar:note-details', [self.id])

    def save(self, *args, **kwargs):
        """
        Fill 'created' and 'modified' attributes on first create
        """
        if self.created is None:
            self.created = tz_now()
        
        if self.modified is None:
            self.modified = self.created
            
        super(Note, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")
