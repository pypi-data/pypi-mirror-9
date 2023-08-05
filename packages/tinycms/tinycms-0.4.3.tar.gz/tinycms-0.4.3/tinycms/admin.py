from django.contrib import admin
from django.conf import settings

from mptt.admin import MPTTModelAdmin

from models import *


class ContentInline(admin.StackedInline):
    model = Content
    extra = 0

class PageAdmin(MPTTModelAdmin):
    inlines = [ContentInline]

#admin.site.register(Page,MPTTModelAdmin)
admin.site.register(Page,PageAdmin)

class ContentAdmin(admin.ModelAdmin):
    list_display  = ['page','value_name']
admin.site.register(Content,ContentAdmin)


def register(inlineClass,index=-1):
    if(index==-1):
        PageAdmin.inlines.append(inlineClass)
    else:
        PageAdmin.inlines.insert(index,inlineClass)




