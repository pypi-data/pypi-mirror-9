from autobreadcrumbs import site
from django.utils.translation import ugettext_lazy

site.update({
    'bazar:index': ugettext_lazy("Bazar"),
    'bazar:entity-index': ugettext_lazy("Entities"),
    'bazar:entity-for-kind-index': "{{ view.get_kind_display }}",
    'bazar:entity-detail': "{{ entity_instance.name }}",
    'bazar:entity-edit': ugettext_lazy("Edit"),
    'bazar:entity-note-create': ugettext_lazy("Add a note"),
    'bazar:entity-note-detail': "{{ note_instance.title }}",
    'bazar:entity-note-edit': ugettext_lazy("Edit"),
    'bazar:entity-note-delete': ugettext_lazy("Delete"),
    'bazar:tag-note-list': ugettext_lazy("Tag: {{ view.tag.name }}"),
})