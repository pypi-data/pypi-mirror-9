.. _Django: https://www.djangoproject.com/
.. _South: http://south.readthedocs.org/en/latest/
.. _rstview: https://github.com/sveetch/rstview
.. _autobreadcrumbs: https://github.com/sveetch/autobreadcrumbs
.. _django-braces: https://github.com/brack3t/django-braces/
.. _django-crispy-forms: https://github.com/maraujop/django-crispy-forms
.. _Django-CodeMirror: https://github.com/sveetch/djangocodemirror
.. _RestructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
.. _jQuery-Tags-Input: https://github.com/xoxco/jQuery-Tags-Input

Emencia Django Bazar
====================

A Django app to store basic informations about related entities (like customers, suppliers, ourselves, etc..).

Features
********

* Note cards for entities;
* Optional markup into note cards content (default is no markup, `RestructuredText`_ is easily available);
* `Django-CodeMirror`_ usage if markup is used with RestructuredText;
* Assets management with django-assets;
* Templates prototyped with Foundation5;
* Tags for note cards;

Planned for beta stage
**********************

* ☑ Finish full prototyping (index views, detail views, create forms, edit forms, etc..);
* ☑ Cloud tags for notes;
* ☑ Use optional markup for note content and implement RestructuredText+Django-CodeMirror as default shipped;
* ☑ Implement jquery plugin `jQuery-Tags-Input`_ for tag input into note forms;
* ☑ Better asset management with optional django-assets usage;
* ☑ Use Compass+SCSS for CSS stuff;
* ☐ File(s?) attachment(s?) into note (making content not required nor the attachment but need a validation of at least one is filled). Probably with its own model (not filebrowser) because this should be protected documents, not shareable;
* ☐ Add permissions usage, not every one should be able to see notes, but just for entities adresses&phone why not;
* ☐ Documentation;

Links
*****

* Download his `PyPi package <http://pypi.python.org/pypi/emencia-django-bazar>`_;
* Clone it on his `Github repository <https://github.com/sveetch/emencia-django-bazar>`_;
