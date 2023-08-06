# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin_xtra_widgets.views',
    url(r'^admin_obj_page/(?P<obj_app>\w+)/(?P<obj_class>\w+)/(?P<obj_id>\d+)',
        'open_admin_obj', name='admin_xtra_widgets_open_obj'),
)

