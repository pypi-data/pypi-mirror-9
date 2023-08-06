from django.contrib.auth.models import User
from django.db import models
from django.utils.timesince import timeuntil

class DNSProvider(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField('URL', blank=True, \
        help_text="Web address of the provider's DNS control panel")
    comment = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'DNS Provider'

class DomainRegistrar(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField('URL', blank=True, \
        help_text="Web address of the registrar's domain name control panel")
    comment = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Domain Registrar'

class HostingProvider(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField('URL', blank=True, \
        help_text="Web address of the provider's hosting control panel")
    comment = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        verbose_name = 'Hosting Provider'

class Domain(models.Model):
    name = models.CharField('Domain Name', max_length=150, \
        help_text="Name + TLD, e.g. example.com")
    expiry = models.DateField('Expiry Date', blank=True, null=True)
    registrar = models.ForeignKey(DomainRegistrar, blank=True, null=True, \
        verbose_name='Domain Registrar')
    dns = models.ForeignKey(DNSProvider, blank=True, null=True, \
        verbose_name='DNS Provider')
    client_owned = models.BooleanField('Client Owned', default=False, \
        help_text="""A note to self: is someone else responsible for this
        domain name?""")
    let_expire = models.BooleanField('Let Expire', default=False, \
        help_text="A note to self: are we happy not to renew this domain?")
    comment = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return self.name

    def dns_link(self):
        if self.dns is None:
            return 'n/a'
        else:
            if len(self.dns.url.strip()) > 0:
                return '%s (<a href="%s" target="_blank">go</a>)' % \
                    (self.dns, self.dns.url)
            else:
                return self.dns
    dns_link.allow_tags = True
    dns_link.short_description = 'DNS Provider'
    dns_link.admin_order_field = 'dns'

    def expiry_countdown(self):
        if self.expiry is None:
            return 'n/a'
        else:
            return '%s (%s)' % (self.expiry, timeuntil(self.expiry))
    expiry_countdown.short_description = 'Expiry Date'
    expiry_countdown.admin_order_field = 'expiry'

    def registrar_link(self):
        if self.registrar is None:
            return 'n/a'
        else:
            if len(self.registrar.url.strip()) > 0:
                return '%s (<a href="%s" target="_blank">go</a>)' % \
                    (self.registrar, self.registrar.url)
            else:
                return self.registrar
    registrar_link.allow_tags = True
    registrar_link.short_description = 'Domain Registrar'
    registrar_link.admin_order_field = 'registrar'

    class Meta:
        ordering = ('name',)
        verbose_name = 'Domain Name'

class Server(models.Model):
    name = models.CharField(max_length=50, \
        help_text="Memorable server name or identifier")
    ip = models.IPAddressField('IP Address', blank=True)
    host = models.ForeignKey(HostingProvider, verbose_name='Hosting Provider')
    comment = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        if len(self.ip.strip()) == 0:
            return '%s (%s)' % (self.name, self.host)
        else:
            return '%s (%s - %s)' % (self.name, self.host, self.ip)

    def host_link(self):
        if self.host is None:
            return 'n/a'
        else:
            if len(self.host.url.strip()) > 0:
                return '%s (<a href="%s" target="_blank">go</a>)' % \
                    (self.host, self.host.url)
            else:
                return self.host
    host_link.allow_tags = True
    host_link.short_description = 'Hosting Provider'
    host_link.admin_order_field = 'host'

    def ip_link(self):
        if self.ip is None:
            return 'n/a'
        else:
            return '%s (<a href="http://%s" target="_blank">go</a>)' % \
                (self.ip, self.ip)
    ip_link.allow_tags = True
    ip_link.short_description = 'IP Address'
    ip_link.admin_order_field = 'ip'

    class Meta:
        ordering = ('name',)

class Subdomain(models.Model):
    name = models.CharField('Subdomain', blank=True, max_length=100, null=True, \
        help_text="""Subdomain part of the address (if it exists), e.g. for
        'www.example.com', enter 'www'""")
    domain = models.ForeignKey(Domain)
    server = models.ForeignKey(Server)
    comment = models.CharField(blank=True, max_length=255)

    def __unicode__(self):
        return self.name

    def domain_link(self):
        return '%s (<a href="../domain/%s/" target="_blank">view</a>)' % \
            (self.domain, self.domain.id)
    domain_link.allow_tags = True
    domain_link.short_description = 'Domain'
    domain_link.admin_order_field = 'domain'

    def server_link(self):
        return '%s (<a href="../server/%s/" target="_blank">view</a>)' % \
                (self.server, self.server.id)
    server_link.allow_tags = True
    server_link.short_description = 'Server'
    server_link.admin_order_field = 'server'

    def subdomain_link(self):
        if len(self.name.split()) == 0:
            return self.domain
        else:
            return '%s.%s' % (self.name, self.domain)
    subdomain_link.allow_tags = True
    subdomain_link.short_description = 'Subdomain'
    subdomain_link.admin_order_field = 'name'

    class Meta:
        ordering = ('domain__name', 'name',)