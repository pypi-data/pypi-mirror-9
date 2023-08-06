from django.template import Context
from django.template import loader
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response
from comoda.fileclusters.models import *
from comoda import settings
from django.core import serializers
from django.http import HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from django.core import serializers



def _save_session_messages(request, messages, errors):
    request.session['messages']=messages
    request.session['errors']=errors

    request.session.modified = True


def _pop_session_messages(request):
    messages = []
    errors = []
    try:
        messages = request.session['messages']
        request.session['messages']=[]
    except KeyError:
        pass
    try:
        errors = request.session['errors']
        request.session['errors']=[]
    except KeyError:
        pass

    request.session.modified = True

    return messages,errors

def _get_cluster_or_node (request,context_dict={}, cluster_id=None, node_id=None):
    try:
        if not cluster_id:
          cluster_id = _get_parameter(request, "cluster_id")
        cluster = ClusterConffile.objects.get(pk=cluster_id)
        context_dict['cluster']=cluster
    except (Exception):
        cluster_id=None
        cluster=None
    try:
        if not node_id:
          node_id = _get_parameter(request, "node_id")
        node = Component.objects.get(pk=node_id)
        context_dict['node']=node
    except (KeyError, ValueError, Component.DoesNotExist):
        node_id=None
        node=None

    return cluster_id, cluster, node_id, node

def _get_conffile_blocks(request,conffile):
  try:
      return request.session['conffile'][conffile.id]
  except KeyError:
      # _blocks s equal to (blocks, md5sum, stats)
      _blocks=conffile.get_conffile_blocks()
      try:
          request.session['conffile'][conffile.id]=_blocks
      except KeyError:
          request.session['conffile']={}
          request.session['conffile'][conffile.id]=_blocks

      return _blocks

def _get_parameter(request, name):
    if request.POST:
        try:
          return request.POST[name]
        except KeyError:
          pass
    if request.GET:
        try:
          return request.GET[name]
        except KeyError as e:
          raise e

def _context_page_iterator(request,context_dict, list_iterated, index=None,
        count=None):

   context_dict["path"] = request.path

   if not index:
     try:
        index = int(_get_parameter(request, "index"))
        if index < 1:
            index = 1
        context_dict["index"] = index

     except TypeError:
         index = 1
     except KeyError:
         index = 1
     except ValueError:
         index = 1
   else:
     context_dict["index"] = index

   try:
        if not count:
            try:
              count = int(_get_parameter(request, "count"))
            except TypeError:
              count = 1
            except KeyError:
              count = 1
            except ValueError:
              count = 1

        if count < 1:
            count = 5
        context_dict["count"] = count

        if ( index + count) <= len (list_iterated):
          context_dict["next"] = index + count
        if ( index - count) > 0:
          context_dict["previous"] = index - count
        elif index > 1:
          context_dict["previous"] = 1
   except KeyError:
        count = None
   except ValueError:
        count = None


   min_index = index - 1
   if count:
      max_index = count + min_index
   else:
      max_index=None

   return min_index, max_index


def _binding_hooks (view_name, context_dict,*args):
    '''
        for all hooks of this function, we call them using as arguments the
        context_dict and all of the function args.
    '''
    try:
      hooks = settings.VIEW_HOOKS["comoda.fileclusters.views"][view_name]
      for abs_modulename, function in hooks:
          _, modulename = abs_modulename.rsplit('.',1)
          m = __import__(abs_modulename, {}, {}, modulename)
          f = getattr(m,function)
          f(context_dict, *args)
    except KeyError, e:
        pass

def _binding_templatetags_hooks (templatetag_name, res,*args):
    try:
      hooks \
        = settings.TEMPLATETAGS_HOOKS["comoda.fileclusters.templatetags.fileclusters_extras"][templatetag_name]
      for abs_modulename, function in hooks:
          _, modulename = abs_modulename.rsplit('.',1)
          m = __import__(abs_modulename, {}, {}, modulename)
          f = getattr(m,function)
          res = f(res, *args)

    except KeyError, e:
        pass

    return res

def _create_context(request):
    context_dict={}

    cluster_list = ClusterConffile.objects.order_by("name")

    messages,errors = _pop_session_messages(request)
    context_dict['messages']=messages
    context_dict['error_messages']=errors
    context_dict['nav_global']=settings.MENU_BAR
    context_dict['cluster_list']=cluster_list
    context_dict['user']=request.user

    return context_dict


