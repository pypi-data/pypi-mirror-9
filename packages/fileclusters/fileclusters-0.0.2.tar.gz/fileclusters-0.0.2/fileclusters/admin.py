from comoda.fileclusters.models import *
from django.contrib import admin
from django.forms import ModelForm, PasswordInput, CharField

class AgentAdminForm(ModelForm):
    password = CharField(widget=PasswordInput())
    class Meta:
        model = Agent

class AgentAdmin(admin.ModelAdmin):
   form = AgentAdminForm

class ClusterConffileAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                {'fields':  ['name']
                              }),
        ('Extra information', {'fields':  ['description'],
                               'classes': ['collapse']
                              }),
    ]

    list_display = ('name', 'description', 'value')
    list_filter = ['name']
    search_fields = ['name']

class HTTPServiceInline(admin.TabularInline):
    model = HTTPService
    extra = 1


class ComponentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                {'fields':  ['name',
        #                         'cluster', 'master'
                              ]
                              }),
        ('Extra information', {'fields':  ['description'],
                               'classes': ['collapse']
                              }),
    ]

    list_display = ('name', 'description')
    list_filter = ['name']
    search_fields = ['name']

    # inlines = [HTTPServiceInline]

class ConffileAdmin(admin.ModelAdmin):
    # list_display = ('filename', 'description', 'digest')
    list_display = ('filename', 'description')



# admin.site.register(ClusterConffile,ClusterConffileAdmin)
# admin.site.register(Component, ComponentAdmin)
# admin.site.register(Conffile, ConffileAdmin)
# admin.site.register(Agent,AgentAdmin)
# admin.site.register(HTTPService)
# admin.site.register(HTTPAuthData)


