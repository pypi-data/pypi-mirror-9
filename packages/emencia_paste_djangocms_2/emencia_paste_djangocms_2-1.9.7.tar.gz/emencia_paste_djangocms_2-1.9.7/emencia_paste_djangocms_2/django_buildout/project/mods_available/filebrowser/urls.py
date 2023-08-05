# -*- coding: utf-8 -*-

urlpatterns = patterns('',
    url(r'^admin/filebrowser/', include('filebrowser.urls')),
    ) + urlpatterns
