# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext as _
from django import forms
from odnoklassniki_api.admin import OdnoklassnikiModelAdmin
from models import Group

class GroupAdmin(OdnoklassnikiModelAdmin):

    def image_preview(self, obj):
        return u'<a href="%s"><img src="%s" height="30" /></a>' % (obj.pic640x480, obj.pic50x50)
    image_preview.short_description = u'Картинка'
    image_preview.allow_tags = True

    search_fields = ('name',)
    list_display = ('image_preview','name','shortname','ok_link','premium')
    list_display_links = ('name','shortname')
    list_filter = ('premium', 'private', 'shop_visible_admin', 'shop_visible_public')

    exclude = ('users',)

admin.site.register(Group, GroupAdmin)