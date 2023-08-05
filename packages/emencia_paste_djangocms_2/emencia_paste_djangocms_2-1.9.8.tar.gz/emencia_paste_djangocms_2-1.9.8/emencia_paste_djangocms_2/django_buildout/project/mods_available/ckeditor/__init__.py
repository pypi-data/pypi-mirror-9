# -*- coding: utf-8 -*-
"""
Enable the customization of the `CKEditor`_ editor. It is enabled by default and used by `Django CKEditor`_ in the `cms`_ mod, and also in `zinnia`_.

Use "djangocms_text_ckeditor", a djangocms plugin to use CKEditor (4.x) instead of the default one

This mod contains some tricks to enable "django-filebrowser" usage with "image" plugin from CKEditor.

And some contained patches/fixes :

* the codemirror plugin that is not included in djangocms-text-ckeditor;
* Some missed images for the "showblocks" plugin;
* A system to use the "template" plugin (see views.EditorTemplatesListView for more usage details);
* Some patch/overwrites to have content preview and editor more near to Foundation;
"""