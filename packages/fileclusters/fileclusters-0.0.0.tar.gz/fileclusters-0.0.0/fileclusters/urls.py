# from django.conf.urls.defaults import *
from django.conf.urls import *

urlpatterns = patterns('comoda.fileclusters.views',
    (r'^$', 'index',None, 'fileclusters'),

    (r'^(?P<cluster_id>\d+)/$', 'detail',
       None, 'fileclusters-cluster'),

    # URLs related to conffiles:

    (r'^conffile/(?P<conffile_id>\d+)/$', 'conffile_view',
       None, 'fileclusters-conffile'),

    (r'^conffile/(?P<conffile_id>\d+)/delete$', 'conffile_delete',
       None, 'fileclusters-conffile-delete'),

    (r'^conffile/(?P<conffile_id>\d+)/edit$', 'conffile_edit',
       None, 'fileclusters-conffile-edit'),

    (r'^conffile/(?P<conffile_id>\d+)/section/paste$', 'conffile_section_paste',
       None, 'fileclusters-conffile-section-paste'),

    # (r'^conffile/(?P<conffile_id>\d+)/section/copy$', 'conffile_section_copy',
    #   None, 'fileclusters-conffile-section-copy'),

    (r'^conffile/(?P<conffile_id>\d+)/section/add$', 'conffile_section_add',
       None, 'fileclusters-conffile-section-add'),

    (r'^conffile/(?P<conffile_id>\d+)/section/remove$', 'conffile_section_remove',
       None, 'fileclusters-conffile-section-remove'),

    (r'^conffile/(?P<conffile_id>\d+)/update$', 'conffile_update',
       None, 'fileclusters-conffile-update'),

    (r'^conffile/(?P<conffile_id>\d+)/upload$', 'conffile_upload',
       None, 'fileclusters-conffile-upload'),

    # Related to cluster

    (r'^cluster/(?P<cluster_id>\d+)/conffile/add$', 'conffile_add',
        None, 'fileclusters-cluster-conffile-add'),

    (r'^cluster/(?P<cluster_id>\d+)/command/(?P<command>[\w-]+)$',
        'execute_command',
        None, 'fileclusters-cluster-command'),
    # Regular expresion for the command name to execute:
    #
    #     uptime
    #     date
    #     <service>-[start|stop|restart]
    #
    # For example:
    #
    # ... lepg-server-[start|stop|restart|confcheck]
    # ... lepg-provider-[start|stop|restart]
    # ... psi-assembler-server-[start|stop|restart]

    (r'^cluster/(?P<node_id>\d+)/file/cat$',
        'cat_file',
        None, 'fileclusters-cluster-file-cat'),

    # Related to nodes ...

    (r'^node/(?P<node_id>\d+)/$', 'detail',
        None, 'fileclusters-node'),

    (r'^node/(?P<node_id>\d+)/conffile/add$', 'conffile_add',
        None, 'fileclusters-node-conffile-add'),

    (r'^node/(?P<node_id>\d+)/command/(?P<command>[\w-]+)$',
        'execute_command',
        None, 'fileclusters-node-command'),
    # Regular expresion for the command name to execute:
    #
    #     uptime
    #     date
    #     <service>-[start|stop|restart]
    #
    # For example:
    #
    # ... lepg-server-[start|stop|restart|confcheck]
    # ... lepg-provider-[start|stop|restart]
    # ... psi-assembler-server-[start|stop|restart]

    (r'^node/(?P<node_id>\d+)/file/cat$',
        'cat_file',
        None, 'fileclusters-node-file-cat'),


)


