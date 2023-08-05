# -*- coding: utf-8 -*-

INSTALLED_APPS = add_to_tuple(INSTALLED_APPS,
    'django.contrib.comments',
    'tagging',
    'zinnia',
    'cmsplugin_zinnia')

# Enable ckeditor usage for entries editor
ZINNIA_WYSIWYG = "ckeditor"

# List entries by ..
ZINNIA_PAGINATION = 3

TEMPLATE_CONTEXT_PROCESSORS += (
    'zinnia.context_processors.version',)
