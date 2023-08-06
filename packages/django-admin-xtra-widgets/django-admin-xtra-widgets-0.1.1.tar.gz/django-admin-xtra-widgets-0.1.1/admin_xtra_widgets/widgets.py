#-*- coding: utf-8 -*-

from django.contrib.admin.widgets import AdminURLFieldWidget, AdminFileWidget, AdminTextInputWidget, ForeignKeyRawIdWidget, ManyToManyRawIdWidget
from django.forms.widgets import Select
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse
from django.utils.html import escape


class VerboseManyToManyRawIdWidget(ManyToManyRawIdWidget):
    """
    A Widget for displaying ManyToMany ids in the "raw_id" interface rather than
    in a <select multiple> box. Display user-friendly value like the ForeignKeyRawId widget
    """
    def __init__(self, rel, attrs=None, *args, **kwargs):
        super(VerboseManyToManyRawIdWidget, self).__init__(rel, attrs, *args, **kwargs)
        
    def label_for_value(self, value):
        values = value.split(',')
        str_values = []
        key = self.rel.get_related_field().name
        app_label = self.rel.to._meta.app_label
        class_name = self.rel.to._meta.object_name.lower()
        for v in values:
            try:
                obj = self.rel.to._default_manager.using(self.db).get(**{key: v})
                url = reverse('admin:{0}_{1}_change'.format(app_label, class_name), args=[obj.id])
                label = escape(smart_unicode(obj))
                
                x = u'<a href="{0}" {1}>{2}</a>'.format(url,
                    'onclick="return showAddAnotherPopup(this);" target="_blank"',
                    label
                )
                
                str_values += [x]
            except self.rel.to.DoesNotExist:
                str_values += [u'???']
        return u'&nbsp;<strong>{0}</strong>'.format(u',&nbsp;'.join(str_values))


def handle_image_field(self,type,db_field,field_name,**kwargs):
    if db_field.name == field_name:
        kwargs['widget'] = AdminImageWidget
        try:
            del kwargs['request']
        except KeyError:
            pass
        return db_field.formfield(**kwargs)
    return super(type,self).formfield_for_dbfield(db_field, **kwargs)


class EmailFieldWidget(AdminTextInputWidget):
    def render(self, name, value, attrs=None):
        widget = super(EmailFieldWidget, self).render(name, value, attrs)
        if value:
            return mark_safe(
                u'{0}&nbsp;&nbsp;<a href="mailto:{1}">{2}</a>'.format(widget, value, _(u"Write an email"))
            )
        else:
            return widget


class SelectAndLinkWidget(Select):
    add_button_template = """
        <a onclick="return showAddAnotherPopup(this);" class="add-another"
        href="{0}">
        <img height="10" width="10" alt="{1}" src="/files/admin/img/admin/icon_addlink.gif">
        </a>
    """

    def render(self, name, value, attrs=None):
        widget = super(SelectAndLinkWidget, self).render(name, value, attrs)
        admin_url = reverse('admin:{0}_{1}_add'.format(self.obj_app, self.obj_class))
        self.add_button = self.add_button_template.format(admin_url, _(u"Open another"))
        html = u'{0}&nbsp;&nbsp;{1}'.format(widget, self.add_button)
        if value:
            url = reverse(
                'admin_xtra_widgets_open_obj',
                kwargs={'obj_app': self.obj_app, 'obj_class': self.obj_class, 'obj_id': value}
            )

            html += u'&nbsp;&nbsp;<a href="{0}" {1}>Ouvrir</a>'.format(
                url,
                u'onclick="return showAddAnotherPopup(this);" target="_blank"'
            )
        return mark_safe(html)


class ClickableRawIdWidget(ForeignKeyRawIdWidget):
    """
    """
    def __init__(self, rel, attrs=None):
        super(ClickableRawIdWidget, self).__init__(rel, attrs)

    def label_for_value(self, value):
        str_values = []
        key = self.rel.get_related_field().name
        try:
            app_label = self.rel.to._meta.app_label
            class_name = self.rel.to._meta.object_name.lower()
            obj = self.rel.to._default_manager.using(self.db).get(**{key: value})
            url = reverse('admin:{0}_{1}_change'.format(app_label, class_name), args=[value])
            return u'<a href="{0}" {1}>{2}</a>'.format(
                url,
                'onclick="return showAddAnotherPopup(this);" target="_blank"',
                smart_unicode(obj)
            )
        except self.rel.to.DoesNotExist:
            return u'???'


class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        label = _(u"Open the link")
        return mark_safe(
            u'{0}&nbsp;&nbsp;<input type="button" '
            u'value="{2}" onclick="window.'
            u'open(document.getElementById(\'{1}\')'
            u'.value)" />'.format(widget, attrs['id'], label)
        )
