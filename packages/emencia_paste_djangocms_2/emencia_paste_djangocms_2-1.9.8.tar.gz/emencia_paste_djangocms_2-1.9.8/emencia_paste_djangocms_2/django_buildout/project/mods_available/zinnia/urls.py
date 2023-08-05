# -*- coding: utf-8 -*-

urlpatterns = patterns('',
    url(r'^news/', include('zinnia.urls')),
    #url(r'^comments/', include('django.contrib.comments.urls')),
    ) + urlpatterns
