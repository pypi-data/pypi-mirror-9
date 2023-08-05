from django import template
from django.utils import translation
from django.http import Http404#,HttpResponse

from tinycms.models import *

register = template.Library()

"""
@register.tag(name="show_absolute_menu")
def show_absolute_menu(parser, token):
    Page.objects.root_nodes()


class TinycmsMenuAbsolute(template.Node):
    def render(self):
        pass
"""


@register.simple_tag(takes_context=True)
def show_contents(context, value_name,contentTag=None):
    """Show cms content.

    Variables:
    value_name -- value_name of contents to be shown.
    contentTag -- When contentTag is not None, Each content is tagged by contentTag like <contentTag>content</contentTag>
    """
    if(value_name not in context):
        raise Http404
    valList = context[value_name]

    result =""

    for item in valList:
        if(contentTag):
            result += "<%s>%s</%s>" % (contentTag,item,contentTag)
        else:
            result += "%s" % item
    return result

"""
def internal_create_children_menu(item,sublevel,lang):
    result =""
    menuContent = Content.objects.filter(page=item,language=lang,value_name="menu_title")
    if(menuContent.count()!=0):
        result = result + "<li><a href='"+item.get_absolute_url()+"'>"+menuContent[0].render()+"</a>"
        if(sublevel>0):
            if(item.get_children().count()>0):
                result = result +"<ul>"+ create_children_menu(item,sublevel-1,lang) +"</ul>"
        result = result+"</li>"
    return result


def create_children_menu(parent,sublevel,lang):
    result =""
    for item in parent.get_children():
        result = result + internal_create_children_menu(item,sublevel,lang)
    return result


@register.simple_tag(takes_context=True)
def show_absolute_menu(context, sublevel = 0):
    "" "Show absolute menu.  Content of value_name='menu_title' are used.

    "" "
    page_roots = Page.objects.root_nodes()
    result =""

    lang = translation.get_language()

    for item in page_roots:
        result = result + internal_create_children_menu(item,sublevel,lang)
    return result
"""
