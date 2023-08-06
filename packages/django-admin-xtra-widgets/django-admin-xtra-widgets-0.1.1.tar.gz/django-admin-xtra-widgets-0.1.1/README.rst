django-admin-xtra-widgets
===============================================

Overview
------------------------------------
more widgets for the django admin


Quick start
------------------------------------
If you need the SelectAndLink widget
In settings.py, add 'admin_xtra_widgets' to the INSTALLED_APPS 
In urls.py add ``(r'^admin-xtra-widgets/', include('admin_extra_widgets.urls'))`` to your urlpatterns

VerboseManyToManyRawIdWidget
------------------------------------
This widget adds a clickable text value to the usual raw_id widget. It indicates the current values of the field

In your admin

    from admin_xtra_widgets.widgets import VerboseManyToManyRawIdWidget

    class YourAdmin(admin.ModelAdmin):
        #raw_id_fields = ["your_m2m_field"]
        
        def formfield_for_dbfield(self, db_field, **kwargs):
            if db_field.name in ('your_m2m_field', 'other_m2m_field'):
                kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel, self.admin_site)
            else:
                return super(YourAdmin,self).formfield_for_dbfield(db_field,**kwargs)
            kwargs.pop('request')
            return db_field.formfield(**kwargs)



License
=======

django-favman is licensed under the GNU-LGPL

