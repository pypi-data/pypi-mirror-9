
from django.http import Http404

from models import *


def show_page(request,url):
    """Return HttpResponse of url
    """
    return Dispatcher.dispatch(url,request)
    #return page.render(request)



"""
from models import *
def generate_url(node):
    urlpatterns = patterns("")
    if(node.is_active):
        urlpatterns += patterns('',url("^"+node.get_url()+"$","django_tinycms.views.show_page",{"page":node}))
    for item in node.get_children():
        urlpatterns += generate_url(item)
    return urlpatterns


urlpatterns = patterns("")
page_roots = Page.objects.root_nodes()

for item in page_roots:
    urlpatterns += generate_url(item)
"""


