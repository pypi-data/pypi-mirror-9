from django.contrib import admin

from .models import DNSProvider, Domain, DomainRegistrar, \
    HostingProvider, Server, Subdomain

class DNSProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'comment')
admin.site.register(DNSProvider, DNSProviderAdmin)

class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'expiry_countdown', 'registrar_link', \
        'dns_link', 'client_owned', 'let_expire', 'comment')
    list_filter = ('registrar', 'dns', 'client_owned', 'let_expire')
admin.site.register(Domain, DomainAdmin)

class DomainRegistrarAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'comment')
admin.site.register(DomainRegistrar, DomainRegistrarAdmin)

class HostingProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'comment')
admin.site.register(HostingProvider, HostingProviderAdmin)

class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'host_link', 'ip_link', 'comment')
    list_filter = ('host',)
admin.site.register(Server, ServerAdmin)

class SubdomainAdmin(admin.ModelAdmin):
    list_display = ('subdomain_link', 'domain_link', 'server_link', 'comment')
    list_filter = ('server', 'domain', 'server__host', 'domain__dns')
admin.site.register(Subdomain, SubdomainAdmin)