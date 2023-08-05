# -*- coding: utf-8 -*-
import os

INSTALLED_APPS = add_to_tuple(INSTALLED_APPS, 'djangocms_text_ckeditor')

STATICFILES_DIRS += ( os.path.join(MOD_FILE, "static"),)
TEMPLATE_DIRS += (os.path.join(MOD_FILE, "templates"),)

# On redéfinit les settings pour y inclure les affinements de configuration de l'éditeur
CKEDITOR_SETTINGS = {
    'language': '{{ language }}',
    'toolbar': 'CMS',
    'skin': 'moono',
    'toolbarCanCollapse': False,
    'contentsCss': "/static/css/ckeditor.css",
    'toolbar_CMS': [
        ['Undo', 'Redo'],
        ['cmsplugins', '-', 'ShowBlocks'],
        ['Format', 'Styles'],
        #['RemoveFormat', '-', '', 'PasteText', 'PasteFromWord'],
        ['RemoveFormat', '', '', '', ''],
        ['Maximize', ''],
        '/',
        ['Source', '-', 'searchCode', 'autoFormat', '-', 'CommentSelectedRange', 'UncommentSelectedRange', '', ''],
        '/',
        ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript', '', ''],
        ['JustifyLeft', 'JustifyCenter', 'JustifyRight', '', '', '', ''],
        ['Link', 'Unlink'],
        ['Image', '-', 'NumberedList', 'BulletedList', '-', 'Table', '-', 'CreateDiv', 'HorizontalRule', 'SpecialChar', '-', 'Templates'],
        # , 'Iframe' # Disabled because djangocms seems to sanitize it from the posted HTML
    ],
    # Utilise des class CSS de Foundation pour le plugin d'alignement de texte (justify)
    'justifyClasses': [ 'text-left', 'text-center', 'text-right', 'AlignJustify' ],
    # Active par défaut l'affichage de la signalisation des blocs
    'startupOutlineBlocks': True,
    # Case "Remplacer le contenu actuel" décochée par défaut
    'templates_replaceContent': False,
    # Urls du script définissant les templates de contenu
    'templates_files': [
        '/ckeditor/editor_site_templates.js'
    ],
    # Redéfinition pour activer le plugin codemirror
    'extraPlugins': 'cmsplugins,codemirror',
    # Lien pour activer "Explorer le serveur" au travers de django-filebrowser
    'filebrowserBrowseUrl': "/admin/filebrowser/browse?pop=3",
    # Utile pour temporairement désactiver le menu de contexte (clic droit) et plugins 
    # dépendants dans l'éditeur
    #'removePlugins': 'liststyle,tabletools,scayt,menubutton,contextmenu',
}

# Chemin relatif du répertoire contenant les templates de contenu pour l'éditeur
CKEDITOR_EDITOR_TEMPLATES_PATH = "ckeditor/editor-site-templates/"
# Chemin relatif du répertoire contenant la représentation en image du contenu pour 
# l'éditeur
CKEDITOR_EDITOR_TEMPLATES_IMAGES_PATH = "ckeditor/editor-site-templates/"
# Nom de fichier à rechercher pour le manifest des templates de contenu, relatif au 
# chemin de CKEDITOR_EDITOR_TEMPLATES_PATH
CKEDITOR_EDITOR_TEMPLATES_NAMES_FILE = "manifest.json"
# Template string du code Javascript de base où injecter la définition des templates de 
# contenus trouvés
# Empeche les balises auto fermantes de XHTML
CKEDITOR_EDITOR_JS_TEMPLATE = u"""CKEDITOR.addTemplates( 'default', {{imagesPath:"{imagespath}", templates: {json_list}}});"""
