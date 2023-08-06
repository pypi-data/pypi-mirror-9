# -*- coding: utf-8 -*-
"""
Common views
"""
from django.conf import settings
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Count

from braces.views import LoginRequiredMixin

from bazar.models import Entity, Note

class IndexView(LoginRequiredMixin, generic.TemplateView):
    """
    Index view
    """
    template_name = "bazar/index.html"
    
    def get(self, request, *args, **kwargs):
        
        context = {
            # Count entries for each used kind
            'entities_kinds': Entity.objects.values('kind').annotate(num_kinds=Count('kind')),
        }
        
        return self.render_to_response(context)
