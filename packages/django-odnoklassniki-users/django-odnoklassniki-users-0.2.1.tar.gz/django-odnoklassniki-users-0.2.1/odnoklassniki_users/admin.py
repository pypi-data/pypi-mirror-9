# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
from odnoklassniki_api.admin import OdnoklassnikiModelAdmin
from models import User

class UserAdmin(OdnoklassnikiModelAdmin):
    def image_preview(self, obj):
        return u'<a href="%s"><img src="%s" height="30" /></a>' % (obj.pic1024x768, obj.pic50x50)
    image_preview.short_description = u'Аватар'
    image_preview.allow_tags = True

    list_display = ('image_preview','name','ok_link','gender','birthday','city','country','has_email',)
    list_display_links = ('name',)
    list_filter = ('gender','has_email')
    search_fields = ('first_name','last_name',)
#    exclude = ('friends_users',)

admin.site.register(User, UserAdmin)