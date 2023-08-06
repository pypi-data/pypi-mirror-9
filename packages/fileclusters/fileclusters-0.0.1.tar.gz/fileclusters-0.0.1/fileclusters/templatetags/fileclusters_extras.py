from django.template import Library
from django.core.urlresolvers import reverse
from comoda.fileclusters import models
from comoda import settings
from comoda.fileclusters import helpers

register = Library()


def modules():
    res = ""
    res = res + "<ul>"
    for url,name in settings.MENU_BAR:
      res = res + "<li>" + '<a href="' \
        + url \
        + '">' +  name +'</a>' + "</li>"
    res = res + "</ul>"

    return res

register.simple_tag(modules)



def node_item(node):

    if isinstance (node, int):
      node = models.Component.objects.get(pk=node)
    res = '<a href="' + reverse('fileclusters-node',args=[node.id]) + '">' + node.__unicode__() + '</a>'

    res = helpers._binding_templatetags_hooks ("node_item", res, node)

    if node.master:
      res = res + "<strong> (master node) </strong>"
    return res
register.simple_tag(node_item)

def conffile_comments(conffile):

    if isinstance (conffile, int):
      node = models.Conffile.objects.get(pk=conffile)
    res = ""
    first = True
    for child in conffile.childs:
        try:
          for c in child.comment_lines:
            if not first:
              res = res + "\n" + c
            else:
              res = c
              first=False
        except Exception:
            pass
    return res
register.simple_tag(conffile_comments)

def conffile_item(conffile, cluster):

    get_params="?"

    if isinstance (cluster, models.ClusterConffile):
        get_params = "?cluster_id=" + str(cluster.id)
    else:
        get_params = "?node_id=" + str(conffile.component_id)

    if isinstance (conffile, int):
      node = models.Conffile.objects.get(pk=conffile)
    res = '<a href="' + reverse('fileclusters-conffile',args=[conffile.id]) + \
      get_params + '">' + conffile.__unicode__() + '</a>'
    res = res + ' - <a href="' + reverse('fileclusters-conffile',args=[conffile.id]) + \
      get_params + '&format=plain">' + "plain" + '</a>'
    res = res + ' - <a onclick="confirmation(\'' + \
             reverse('fileclusters-conffile-delete',args=[conffile.id]) + \
             get_params + \
             '\')">' + "delete" + '</a>'


    # Actions ...
    # res = res + " - " + '<a href="' \
    # + reverse("fileclusters-conffile-edit",args=[conffile.id]) + '">' + "edit" + '</a>'

    return res
register.simple_tag(conffile_item)

def abs_position(offset, index):
    try:
      res = unicode(int (offset) + int(index) - 1 )
    except Exception:
      res = ""
    return res
register.simple_tag(abs_position)



@register.filter(name='listsort')
def listsort(value):

    def _cmp_sort(x,y):
      """
      Return 1 if x > y, return 0 if x < y and return 0 if x = y
      """
      _eq = str(x) == str(y)
      _min = str(x) < str(y)

      if _eq == True:
        # print str(x) + "==" + str(y)
        return 0
      if _min == True:
        # print str(x) + "<" + str(y)
        return -1
      else:
        # print str(x) + ">" + str(y)
        return 1

    return sorted (value, cmp=_cmp_sort)

