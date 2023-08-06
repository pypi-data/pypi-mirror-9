from django.template import Context
from django.template import loader
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render_to_response

from comoda.fileclusters import helpers
from comoda.fileclusters.models import *
from comoda import settings

from django.core import serializers
from django.http import HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
from django.core import serializers

from django import forms
from django.contrib.auth.decorators import login_required



@login_required
def cat_file(request, cluster_id=None, node_id=None, command=None):
    try:
      filename = helpers._get_parameter(request, "filename")
    except:
      raise Http404
    try:
      nlines = helpers._get_parameter(request, "nlines")
    except:
      nlines=None

    def _get_filelines_list ():
        filelines = ""
        a = node.agent_set.all()[0]
        lines,digest,stats = a.get_file(filename)

        if nlines:
          lines = lines.split("\n")
          for l in lines[:(int(nlines))]:
            filelines = filelines + l + "\n"
        else:
            filelines = lines
        return filelines

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,{},cluster_id,node_id)

    file_lines=""
    if cluster:
        node_list = cluster.component_set.all()
        for n in node_list:
          if n.master:
            node=n
            file_lines = _get_filelines_list ()
            break
    else:
        if node:
            file_lines = _get_filelines_list ()

    return HttpResponse(file_lines, mimetype="text/plain")



@login_required
def detail(request, cluster_id=None, node_id=None):
    if not (cluster_id or node_id):
        raise Http404

    context_dict=helpers._create_context(request)

    helpers._binding_hooks ("detail", context_dict,request,cluster_id,node_id)
    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,context_dict,cluster_id,node_id)

    if cluster:
        node_list = cluster.component_set.all()
        conffile_list=[]
        for n in node_list:
          if n.master:
            conffile_list = n.conffile_set.order_by("filename")
        context_dict['conffile_list']=conffile_list
        return render_to_response('clusters/detail.html', context_dict)
    else:
        try:
            conffile_list = node.conffile_set.all()
            context_dict['conffile_list']=conffile_list
        except Exception, e:
            errors.append(str(e))
        return render_to_response('clusters/detail.html', context_dict)


@login_required
def conffile_add(request,cluster_id=None, node_id=None):

    class ConffileForm(forms.ModelForm):
      class Meta:
          model = Conffile

    context_dict=helpers._create_context(request)

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,context_dict,cluster_id,node_id)

    if request.method == 'POST':
        messages=[]
        errors=[]
        form = ConffileForm(request.POST)
        if form.is_valid():
          node_list=[]
          if cluster:
              node_list = cluster.component_set.all()
          else:
              node_list = [node]

          for n in node_list:
              if (request.POST['Action'] == 'Add'):
                  try:
                    n.conffile_set.create(
                          filename = request.POST["filename"],
                          description = request.POST["description"],
                          parser = request.POST["parser"])

                    messages.append("New conffile has been succesfully added \
in %s" % str(n) )
                  except Exception, e:
                    errors.append(str(e))

          # Making a redirection ...
          if cluster_id:
            redirect_url = reverse('fileclusters-cluster',args=[cluster_id])
          else:
            redirect_url = reverse('fileclusters-node',args=[node_id])
          helpers._save_session_messages(request, messages, errors)
          return HttpResponsePermanentRedirect(redirect_url)

        # Else ...
        errors.append("New conffile submited has not been added.")

        redirect_url = reverse('fileclusters-cluster',args=[cluster_id])
        if not cluster_id:
           redirect_url = reverse('fileclusters-node',args=[node_id])
        helpers._save_session_messages(request, messages, errors)
        return HttpResponsePermanentRedirect(redirect_url)

    else:
        # Show a form ...
        messages,errors = helpers._pop_session_messages(request)
        template = "clusters/conffile_add_form.html"
        context_dict['form']=ConffileForm()
        return render_to_response(template,context_dict)

@login_required
def conffile_delete(request,conffile_id=None):

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request)

    messages=[]
    errors=[]
    node_list=[]

    if cluster:
       try:
          conffile = Conffile.objects.get(pk=conffile_id)
          _f=conffile.filename
          # c1 is a component (aka node)
          for c1 in cluster.component_set.iterator():
             # c2 is a conffile
             for c2 in c1.conffile_set.iterator():
               if c2.filename == conffile.filename:
                 try:
                   c2.delete()
                   messages.append("Configuration file %s deleted in %s node." % (_f, c1))
                 except Error as e:
                   errors.append(str(e))

       except (KeyError, ClusterConffile.DoesNotExist):
           errors.append("Conffile %s not found." % str(conffile_id))
       except Exception, e:
           errors.append(str(e))

    else:
        try:
          conffile = Conffile.objects.get(pk=conffile_id)
          _f = conffile.filename
          conffile.delete()
          messages.append("Conffile %s has been succesfully deleted" % str(_f) )

        except (KeyError, ClusterConffile.DoesNotExist):
            errors.append("Conffile %s not found." % str(conffile_id))
        except Exception, e:
            errors.append(str(e))

    # Making a redirection ...
    if cluster_id:
        redirect_url = reverse('fileclusters-cluster',args=[cluster_id])
    else:
        redirect_url = reverse('fileclusters-node',args=[node_id])
    helpers._save_session_messages(request, messages, errors)
    return HttpResponsePermanentRedirect(redirect_url)


@login_required
def conffile_view(request,conffile_id=None):
    context_dict=helpers._create_context(request)

    conffile = Conffile.objects.get(pk=conffile_id)

    try:
      _format = helpers._get_parameter(request, "format")
      if _format == "plain":

        file_lines, _, _ =conffile.get_conffile_raw()
        context_dict['file_lines']=file_lines
        return HttpResponse(file_lines, mimetype="text/plain")

    except KeyError, e:
        pass

    context_dict['conffile']=conffile

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,context_dict)

    # Reinizialization of conffile list. 
    try:
        _blocks,_md5,_stats=conffile.get_conffile_blocks()
        context_dict['conffile_blocks']=_blocks
        context_dict['conffile_stats'] =_stats
        context_dict['conffile_md5'] =_md5
        try:
          request.session['conffile'][conffile.id]=(_blocks,_md5,_stats)
        except KeyError:
          request.session['conffile']={}
          request.session['conffile'][conffile.id]=(_blocks,_md5,_stats)
    except Error as e:
        errors.append(str(e))

    request.session.modified = True

    template = conffile.get_default_template("VIEW_FILE")
    return render_to_response(template, \
           context_dict)

@login_required
def conffile_edit(request,conffile_id=None):
    context_dict=helpers._create_context(request)

    conffile = Conffile.objects.get(pk=conffile_id)
    context_dict['conffile']=conffile

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,context_dict)

    conffile_blocks,conffile_md5,conffile_stats \
            = helpers._get_conffile_blocks(request,conffile)

    min_index,max_index = helpers._context_page_iterator(request, context_dict,
            conffile_blocks)

    context_dict['conffile_stats']= conffile_stats
    context_dict['conffile_md5']= conffile_md5
    context_dict['conffile_blocks']= \
            conffile_blocks[min_index:max_index]
    template = conffile.get_default_template("EDIT_FILE")
    return render_to_response(template, \
           context_dict)

@login_required
def conffile_upload(request,conffile_id=None):

    conffile = Conffile.objects.get(pk=conffile_id)

    errors=[]
    messages=[]

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request)

    conffile_blocks=None

    if (len(request.POST)>1) and request.FILES.has_key("datafile"):
         file_lines = request.FILES["datafile"].read()

         if cluster:
           # c1 is a component (aka node)
           for c1 in cluster.component_set.iterator():
             # c2 is a conffile
             for c2 in c1.conffile_set.iterator():
               if c2.filename == conffile.filename:
                 try:
                   c2.save_conffile_from_raw(file_lines)
                   messages.append("Configuration file %s modified in %s node." % (c2, c1))
                 except Error as e:
                   errors.append(str(e))
         else:
           # No cluster found ...
           try:
             conffile.save_conffile_from_raw(file_lines)
             messages.append("Configuration file %s modified" % conffile)
           except Error as e:
             errors.append(str(e))
    else:
         errors.append("No datafile received")

    helpers._save_session_messages(request, messages, errors)

    # Making a redirection ...
    get_params=""
    if cluster_id:
        get_params = "?cluster_id=" + str(cluster.id)

    redirect_url = reverse('fileclusters-conffile',args=[conffile.id]) + \
             get_params

    return HttpResponsePermanentRedirect(redirect_url)



@login_required
def conffile_update(request,conffile_id=None):
    context_dict=helpers._create_context(request)
    messages = context_dict["messages"]
    errors = context_dict["error_messages"]

    template =""
    conffile = Conffile.objects.get(pk=conffile_id)
    context_dict['conffile']=conffile

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,context_dict)

    conffile_blocks=None
    try:
      if (len(request.POST)>0):
         conffile_blocks,_,_ =  helpers._get_conffile_blocks(request,conffile)
         conffile.update_section_blocks(request.POST, conffile_blocks)

         if cluster:
           for c1 in cluster.component_set.iterator():
             for c2 in c1.conffile_set.iterator():
               if c2.filename == conffile.filename:
                 try:
                   c2.save_conffile_blocks(conffile_blocks)
                   messages.append("Configuration file %s modified in %s node." % (c2, c1))
                 except Error as e:
                   errors.append(str(e))

         else:
           # No cluster found ...
           conffile.update_section_blocks(request.POST, conffile_blocks)

           try:
             # for i in conffile_blocks:
             #     print "-------"
             #     try:
             #        print i.data
             #     except:
             #        print i.comment_lines

             conffile.save_conffile_blocks(conffile_blocks)
             messages.append("Configuration file %s modified" % conffile)
           except Error as e:
             errors.append(str(e))
      else:
         conffile_blocks,_,_ =  helpers._get_conffile_blocks(request,conffile)
         errors.append("No data to send")
    except TypeError,e:
         errors.append(str(e))
         context_dict['conffile_blocks']=conffile_blocks
         template = conffile.get_default_template("VIEW_FILE")
         return render_to_response(template, \
             context_dict)
    except ValueError,e:
         errors.append(str(e))
         context_dict['conffile_blocks']=conffile_blocks
         template = conffile.get_default_template("VIEW_FILE")
         return render_to_response(template, \
             context_dict)



    # _get_conffile_blocks force get the section_blocks in the session.
    context_dict['conffile_blocks']=conffile_blocks

    template = conffile.get_default_template("VIEW_FILE")

    return render_to_response(template, \
             context_dict)


@login_required
def conffile_section_paste(request,conffile_id=None):

    template =""
    conffile = Conffile.objects.get(pk=conffile_id)

    messages,errors = helpers._pop_session_messages(request)

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request)

    conffile_blocks,_,_ =  helpers._get_conffile_blocks(request,conffile)

    try:
      section_block_list = request.session['copy_and_paste_buffer']
    except Exception. e:
      errors.append("Nothing to paste")
      section_block_list = []

    index=1
    try:
        position=helpers._get_parameter(request,u'position')
    except:
        position=None
    if position:
        position = int (position) - 1
        index = int (position)
        _aux = position
        for s in section_block_list:
            conffile_blocks.insert(_aux,s)
            _aux = _aux + 1
            messages.append("Section %s has been succesfully added." %
                unicode(s))
        messages.append("%s new sections has been succesfully added from %s position" %
            (str(len(section_block_list)),str(position)))
    else:
        for s in section_block_list:
            conffile_blocks.append(s)
            messages.append("Section %s has been succesfully added." %
                unicode(s))
        messages.append("%s new sections has been succesfully added at the end" %
            (str(len(section_block_list))))

    request.session.modified = True

    # Making a redirection ...
    get_params="?"
    if cluster_id:
        get_params = get_params + "cluster_id=" + str(cluster.id)
    get_params = get_params + "&index=" + str(index) + "&count=15"

    redirect_url = reverse('fileclusters-conffile-edit',args=[conffile.id]) + \
        get_params
    helpers._save_session_messages(request, messages, errors)
    return HttpResponsePermanentRedirect(redirect_url)


@login_required
def conffile_section_add(request,conffile_id=None):
    context_dict=helpers._create_context(request)
    template =""
    conffile = Conffile.objects.get(pk=conffile_id)
    context_dict['conffile']=conffile

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,context_dict)

    # _get_conffile_blocks force get the section_blocks in the session.
    conffile_blocks,_,_ =  helpers._get_conffile_blocks(request,conffile)

    if request.POST.has_key("Action"):

      if (request.POST['Action'] == 'Cancel'):
           # Making a redirection ...
           get_params=""
           if cluster_id:
             get_params = "?cluster_id=" + str(cluster.id)
             get_params = get_params + "&index=1&count=15"

           redirect_url = reverse('fileclusters-conffile-edit',args=[conffile.id]) + \
             get_params

           return HttpResponsePermanentRedirect(redirect_url)


      if (request.POST['Action'] == 'Confirm'):
           section_block = conffile.create_section_block(request.POST)

           index=1
           if request.POST.has_key(u'position'):
               position = int (request.POST[u'position']) - 1
               index = int (request.POST[u'position'])
               conffile_blocks.insert(position, section_block)
           else:
               conffile_blocks.append(section_block)

           request.session.modified = True

           messages.append("New section has been succesfully added.")

           # Making a redirection ...
           get_params="?"
           if cluster_id:
             get_params = get_params + "cluster_id=" + str(cluster.id)

           get_params = get_params + "&index=" + str(index) + "&count=15"

           redirect_url = reverse('fileclusters-conffile-edit',args=[conffile.id]) + \
             get_params

           helpers._save_session_messages(request, messages, errors)

           return HttpResponsePermanentRedirect(redirect_url)


    # Else ...
    #
    # only show the section add form and create a block with default values
    # to show as default values.
    template = conffile.get_default_template("ADD_SECTION")

    try:
        context_dict['position']= \
             helpers._get_parameter(request,'position')
    except KeyError:
        pass

    section_block = conffile.create_new_section_block()
    context_dict['conffile_block']=section_block

    context_dict['new_conffile_block']=True

    if request.GET.has_key(u'position'):
      context_dict['position']=request.GET[u'position']

    return render_to_response(template, \
           context_dict)


@login_required
def conffile_section_remove(request,conffile_id=None):
    template =""
    conffile = Conffile.objects.get(pk=conffile_id)

    errors=[]
    messages=[]

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request)

    # _get_conffile_blocks force get the section_blocks in the session.
    conffile_blocks,_,_ =  helpers._get_conffile_blocks(request,conffile)

    try:
        position =  helpers._get_parameter(request,u'position')
        index=position
        position = int (position) - 1
        e = conffile_blocks.pop(position)
        messages.append("Removed %s element" % e.__unicode__())
        request.session.modified = True
    except KeyError, e:
        errors.append("No position selected")
        index=1

    # Making a redirection ...
    get_params="?"
    if cluster_id:
        get_params = get_params + "cluster_id=" + str(cluster.id)
    get_params = get_params + "&index=" + str(index) + "&count=15"

    redirect_url = reverse('fileclusters-conffile-edit',args=[conffile.id]) + \
      get_params

    helpers._save_session_messages(request, messages, errors)
    return HttpResponsePermanentRedirect(redirect_url)


@login_required
def execute_command(request, cluster_id=None, node_id=None, command=None):

    class OutgoingMessage:
      def __init__(self, node, command, output, error, related_cluster=None):
          self.node = node
          self.output = output
          self.error = error
          self.related_cluster = related_cluster
          self.command = command

    context_dict=helpers._create_context(request)

    cluster_id,cluster,node_id,node = \
        helpers._get_cluster_or_node(request,context_dict,cluster_id,node_id)

    if cluster:
        context_dict["return_to"] = reverse('fileclusters-cluster',args=[cluster.id])
    else:
        context_dict["return_to"] = reverse('fileclusters-node',args=[node_id])

    results=[]
    context_dict['result_list']=results

    helpers._binding_hooks ("execute_command",
            context_dict,request,cluster_id, node_id,command)

    command_to_execute=""
    if command == "uptime":
        command_to_execute="uptime"
    if command == "date":
        command_to_execute="date"

    if not command_to_execute == "":
      if cluster_id:
        try:
            node_list = ClusterConffile.objects.get(pk=cluster_id).component_set.all()
        except (KeyError, ClusterConffile.DoesNotExist):
            pass

      else:
        try:
            node = Component.objects.get(pk=node_id)
            node_list = [node]
        except (KeyError, Component.DoesNotExist):
            pass

      for n in node_list:
        a = n.agent_set.all()[0]
        output,error = a.execute_command(command_to_execute)
        result = OutgoingMessage(n,command_to_execute,output,error,cluster)
        results.append(result)

    return render_to_response('clusters/action_result.html', context_dict)

@login_required
def index(request):

    context_dict=helpers._create_context(request)

    _format = helpers._get_parameter(request, "format")
    if _format == "json":

      #if 'application/json' in request.META.get('HTTP_ACCEPT'):
      return HttpResponse(serializers.serialize("json",
            cluster_list),
            mimetype='application/json')

    t = loader.get_template('clusters/index.html')
    c = Context(context_dict)
    return HttpResponse(t.render(c))


    # or, ...
    #
    #    return render_to_response('clusters/index.html', \
    #       {'latest_cluster_list': latest_poll_list})


