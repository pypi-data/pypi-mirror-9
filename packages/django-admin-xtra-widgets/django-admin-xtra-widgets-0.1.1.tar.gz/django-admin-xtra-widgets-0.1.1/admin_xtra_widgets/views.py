# -*- coding: utf-8 -*-

from django.http import HttpResponseRedirect

def open_admin_obj(request, obj_app, obj_class, obj_id):
    url = '/admin/{0}/{1}/{2}/'.format(obj_app, obj_class, obj_id)
    return HttpResponseRedirect(url)