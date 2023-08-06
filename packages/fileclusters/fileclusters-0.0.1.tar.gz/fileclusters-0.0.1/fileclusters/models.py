from django.db import models
import paramiko
import os
import hashlib
from django.conf import settings
import chardet
import socket
import Crypto

def atfork():
    print "Dummy function"

try:
  v = Crypto.__version__
  if v.count(".")>1:
      v = v.split(".")[0] + "." + v.split(".")[1]
  if float(v) > 2.1:
      from Crypto.Random import atfork
except Exception,e:
  print "Exception loading atfork: %s" % e

from django.utils.translation import ugettext_lazy as _

SERVER_TYPE_CHOICES = [
    ('fullApp', _('Full application')),
    ('appWithoutDelivery', _('Application without delivery')),
    ('sourceOnly', _('Source only')),
]

SERVICE_CONF_SOURCE_TYPE_CHOICES = [
    ('none', _('None')),
    ('svn', _('SVN')),
    ('rsync', _('rsync')),
]

SSL_PROXY_X509_AUTH_SERVICE_TYPE_CHOICES = [
    ('nginx', _('Nginx')),
]

USER_PERMISSSION_TYPE_CHOICES = [
    ('ro', _('ro')),
    ('no', _('no')),
    ('rw', _('rw')),
]


class Error(Exception):
    def __init__(self, value, _object):
        self.value = value
        self._object = _object
    def __str__(self):
        return str(self._object) + " - " + repr(self.value)


class ClusterConffile(models.Model):
    class Meta:
        verbose_name = 'Cluster'

    name = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    # TODO:
    value = 100

    def __unicode__(self):
        return self.name

class Component(models.Model):
    class Meta:
        verbose_name = 'Component'

    cluster = models.ForeignKey(ClusterConffile, null=True, blank=True)
    name = models.CharField(max_length=200, null=True,
            blank=True, default="")
    description = models.TextField(max_length=500, null=True,
            blank=True,default="")
    master = models.BooleanField()

    def __unicode__(self):
        return self.name

class Agent(models.Model):
    components = models.ManyToManyField(Component)

    hostname = models.CharField(max_length=1024)
    port = models.IntegerField()

    username = models.CharField(max_length=1024)
    password = models.CharField(max_length=1024)

    description = models.TextField(max_length=1024)

    ssh = paramiko.SSHClient()
    # ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh",
    #         "known_hosts")))
    ssh.set_missing_host_key_policy (paramiko.AutoAddPolicy())

    encoding="Unknown"

    def __unicode__(self):
        return self.username + "@" + self.hostname

    def get_file(self, filename):
        '''
        return (lines, digest, stats)
        '''
        try:
          atfork()
          self.ssh.connect(self.hostname, port=self.port, username=str(self.username),
                password=str(self.password))

          sftp = self.ssh.open_sftp()
          stats = sftp.stat(filename)
          # Stats attributes:
          #   st_atime
          #   st_gid
          #   st_mode
          #   st_mtime
          #   st_uid
          #   st_size
          # 
          # utc = datetime.datetime.utcfromtimestamp(stats.st_mtime)
          # print utc.isoformat()

          remote_file = sftp.file(filename, "r")
          remote_file.set_pipelined(True)
          remote_file_lines = remote_file.read()
          sftp.close()
          self.ssh.close()

          self.encoding = chardet.detect(remote_file_lines)['encoding']

          return remote_file_lines, \
            hashlib.md5(remote_file_lines).hexdigest(), stats
        # except Exception as e:
        except socket.gaierror as e:
            raise Error(str(e), self)

    def save_file(self, filename, lines):
       try:
         atfork()
         self.ssh.connect(self.hostname, port=self.port, username=str(self.username),
                password=str(self.password))
         sftp = self.ssh.open_sftp()

         remote_file = sftp.file(filename, "r")
         remote_file.set_pipelined(True)
         remote_file_lines = remote_file.read()
         encoding = chardet.detect(remote_file_lines)['encoding']

         lines=lines.encode(encoding)

         sftp.open(filename, 'w').write(lines)

         sftp.close()
         self.ssh.close()

       except socket.gaierror as e:
            raise Error(str(e), self)

    def execute_command(self, command):
       try:
         atfork()
         self.ssh.connect(self.hostname, port=self.port, username=str(self.username),
                password=str(self.password))

         i,o,e = self.ssh.exec_command(command)
         output = o.readlines()
         error = e.readlines()
         self.ssh.close()

       except socket.gaierror as e:
            raise Error(str(e), self)

       return output,error

conffile_choices=()
try
    conffile_choices = settings.CONFFILE_TYPES
except Exception:
    conffile_choices=()

class Conffile(models.Model):
    component = models.ForeignKey(Component)
    filename = models.CharField(max_length=1024)
    description = models.TextField(max_length=1024)

    parser = models.CharField(max_length=512,
             choices=conffile_choices
             )

    # TODO: Currently this cache is not being emptying.
    blocks_cache = {}
    #  { conffile.id:{md5sum:blocks, ... }, ... }

    def digest(self):
        agent = self.component.agent_set.all()[0]
        (_,result,_) = agent.get_file(self.filename)
        return result

    def stats(self):
        agent = self.component.agent_set.all()[0]
        (_,_,result) = agent.get_file(self.filename)
        return result

    def view(self):
        agent = self.component.agent_set.all()[0]
        (result,_,_) = agent.get_file(self.filename)
        return result

    def get_default_template(self, template_action):
        abs_modulename = self.parser
        _, modulename = abs_modulename.rsplit('.',1)
        m = __import__(abs_modulename, {}, {}, modulename)
        return m.TEMPLATES[template_action]

    def get_conffile_raw(self):
        agent = self.component.agent_set.all()[0]
        (file_lines,md5,stats) = agent.get_file(self.filename)

        return file_lines, md5, stats

    def get_conffile_blocks(self):
        agent = self.component.agent_set.all()[0]
        (file_lines,md5,stats) = agent.get_file(self.filename)

        try:
          return self.blocks_cache[self.id][md5]
        except KeyError:
          abs_modulename = self.parser
          _, modulename = abs_modulename.rsplit('.',1)
          m = __import__(abs_modulename, {}, {}, modulename)
          try:
            blocks = m.convert_to_internal_representation(file_lines)
            try:
              self.blocks_cache[self.id][md5]=(blocks,md5,stats)
            except KeyError:
              self.blocks_cache[self.id]={}
              self.blocks_cache[self.id][md5]=(blocks,md5,stats)
          except Exception, e:
            raise Error(str(e), self)

          return blocks,md5,stats

    def save_conffile_blocks(self, blocks):
        abs_modulename = self.parser
        _, modulename = abs_modulename.rsplit('.',1)
        m = __import__(abs_modulename, {}, {}, modulename)
        file_lines = m.convert_to_file_format(blocks)

        agent = self.component.agent_set.all()[0]
        agent.save_file(self.filename, file_lines)

    def save_conffile_from_raw(self, file_lines):
        '''
        Save the content of file_lines into the remote file, if the new
        content is rigth formatted.

        file_lines must be a string with '\n' breakline character. It isnt a
        list of strings.
        '''
        abs_modulename = self.parser
        _, modulename = abs_modulename.rsplit('.',1)
        m = __import__(abs_modulename, {}, {}, modulename)

        try:
            blocks = m.convert_to_internal_representation(file_lines)
            file_lines = m.convert_to_file_format(blocks)

            agent = self.component.agent_set.all()[0]
            agent.save_file(self.filename, file_lines)
        except Exception, e:
            raise Error(str(e), self)

    def create_new_section_block(self):
        abs_modulename = self.parser
        _, modulename = abs_modulename.rsplit('.',1)
        m = __import__(abs_modulename, {}, {}, modulename)

        section_block  = m.create_new_section_block()

        return section_block


    def create_section_block(self, section_data_dict):
        abs_modulename = self.parser
        _, modulename = abs_modulename.rsplit('.',1)
        m = __import__(abs_modulename, {}, {}, modulename)

        section_block  = m.create_section_block(section_data_dict)

        return section_block

    def create_section_blocks(self, section_data_dict):
        abs_modulename = self.parser
        _, modulename = abs_modulename.rsplit('.',1)
        m = __import__(abs_modulename, {}, {}, modulename)

        section_blocks  = m.create_section_blocks(section_data_dict)

        return section_blocks

    def update_section_blocks(self, section_data_dict, conffile_blocks):
        abs_modulename = self.parser
        _, modulename = abs_modulename.rsplit('.',1)
        m = __import__(abs_modulename, {}, {}, modulename)

        section_blocks  = m.update_section_blocks(section_data_dict,
                conffile_blocks)

        return section_blocks

    def __unicode__(self):
        return self.filename + " (" + self.parser + ")"

class ConffileBlock:
    '''
    refer_name is a friendly reference to this ConffileBlock

    data attribute contain information storaged inside. For
    example, if block is a option: IP value, port number, names, ...

    Normally, we want storage info like a string.

    It's not usually, but, ocasinally, data attribute can be any other
    object as a dict, tuple or others.
    '''

    particular = False
    refer_name = None
    data = None

    def get_conffile(self):
        if self.parent:
            return self.parent.get_conffile()
        else:
            return self._conffile

    def set_conffile(self, conffile):
        if self.parent:
            self.parent.set_conffile(conffile)
        else:
            self._conffile = conffile

    conffile = property(get_conffile, set_conffile)

    def get_parent(self):
        return self._parent

    def set_parent(self, parent):
        parent.childs.append(self)
        self._parent = parent
    parent = property(get_parent, set_parent)

    def __unicode__(self):
       return unicode(self.refer_name) + ": " + unicode(self.data)


class ConffileBlockOption(ConffileBlock):
    pass

class ConffileBlockComment(ConffileBlock):
    '''
    comment_lines = []. for example:

        comment_lines = ["first line ...","... end line."]
    '''

    comment_lines = None
    def __init__(self):
        self.comment_lines = []

    def __unicode__(self):
        return str(self.comment_lines)


class ConffileBlockInclude(ConffileBlock):
    included_file = None

class ConffileBlockSection(ConffileBlock):
    childs = None

    def __init__(self):
        self.childs = []

class HTTPService(models.Model):
    class Meta:
        verbose_name = 'Service HTTP'

    component = models.ForeignKey(Component)
    auth_method = models.CharField(max_length=200)
    url_basename = models.CharField(max_length=200)

    def __unicode__(self):
        return self.component.__unicode__() + u': ' + self.url_basename

    def status(self):
        return "UNKNOW"

class HTTPAuthData(models.Model):
    class Meta:
        verbose_name = 'Auth. data'

    http_service = models.ForeignKey(HTTPService)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return self.http_service.__unicode__() + u': ' + self.key

class ServiceUser(models.Model):
    class Meta:
        verbose_name = 'Service user'
    name = models.CharField(max_length=1000)
    revocated = models.BooleanField(default=False)
    caid = models.PositiveSmallIntegerField()
    privatekey = models.TextField()
    publickey = models.TextField()
    passp12 = models.CharField(max_length=1000)
    passauth = models.CharField(max_length=1000)

    email = models.EmailField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

class Service(models.Model):
    class Meta:
        verbose_name = 'Service'

    component = models.ForeignKey(Component)

    urischeme = models.CharField(max_length=10)
    urihost = models.CharField(max_length=50)
    uriport = models.PositiveSmallIntegerField()
    uripath = models.CharField(max_length=1000)
    serverdir = models.CharField(_("Server directory"), max_length=1000)
    servertype = models.CharField(_("Server type"), choices=SERVER_TYPE_CHOICES,
            default='fullApp',max_length=1000)
    enabled = models.BooleanField(default=False)

    passfile = models.CharField(max_length=1000)
    passfileperm = models.PositiveSmallIntegerField()
    passfileowner = models.CharField(max_length=1000)

    revocatefile = models.CharField(max_length=1000)
    revocatefileperm = models.PositiveSmallIntegerField()
    revocatefileowner = models.CharField(max_length=1000)



class UserPermission(models.Model):
    class Meta:
        verbose_name = 'User permission'
    user = models.ForeignKey(ServiceUser)
    service = models.ForeignKey(Service)
    directory = models.CharField(max_length=1000)
    mode = models.CharField(_("Modes"), choices=USER_PERMISSSION_TYPE_CHOICES,
            default='ro',max_length=1000)


class ApacheSVNService(Service):
    class Meta:
        verbose_name = 'Apache SVN service'

    svnpassfile = models.CharField(_("SVN passfile"),max_length=1000)
    svnpassfileperm = models.PositiveSmallIntegerField(_("SVN passfile permissions"),max_length=1000)
    svnpassfileowner = models.CharField(_("SVN passfile owner"),max_length=1000)


class SSLProxyX509AuthService(Service):
    class Meta:
        verbose_name = 'SSL proxy X509 Authentication Service'

    delegate = models.ForeignKey(Service, related_name="delegate")
    server_type = models.CharField(_("Server type"),
            choices=SSL_PROXY_X509_AUTH_SERVICE_TYPE_CHOICES,
            default='nginx',max_length=1000)

    serverpass = models.CharField(max_length=1000)

class ServiceConfSource(models.Model):
    class Meta:
        verbose_name = 'Service Configuration Source'

    service_conf_source_type = models.CharField(_("Server configuration source type"),
            choices=SERVICE_CONF_SOURCE_TYPE_CHOICES,
            default='none',max_length=1000)

    address = models.CharField(max_length=1000)
    port = models.PositiveSmallIntegerField()
    directory = models.CharField(max_length=1000)
    user = models.CharField(max_length=1000)
    password = models.CharField(max_length=1000)


