import logging
import inject
from mcloud.application import ApplicationController
from mcloud.events import EventBus
from mcloud.plugins import Plugin
import os
from twisted.internet.defer import inlineCallbacks
from twisted.python import log

HAPROXY_TPL = """
global
        log /dev/log    local0
        log /dev/log    local1 notice
        chroot /var/lib/haproxy
        user haproxy
        group haproxy
        daemon

defaults
        log     global
        option  dontlognull
        timeout connect 5000
        timeout client 50000
        timeout server 50000

        errorfile 400 /etc/haproxy/errors/400.http
        errorfile 403 /etc/haproxy/errors/403.http
        errorfile 408 /etc/haproxy/errors/408.http
        errorfile 500 /etc/haproxy/errors/500.http
        errorfile 502 /etc/haproxy/errors/502.http
        errorfile 503 /etc/haproxy/errors/503.http
        errorfile 504 /etc/haproxy/errors/504.http


{% if ssl_apps %}
frontend http_ssl_proxy
  mode tcp
  bind 0.0.0.0:443

  tcp-request inspect-delay 5s
  tcp-request content accept if { req_ssl_hello_type 1 }

  {% for app in ssl_apps %}
  {% for domain in app.domains %}
  acl is_ssl_{{ app.name }} req_ssl_sni -i {{ domain }}
  {% endfor %}
  use_backend backend_ssl_{{ app.name }}_cluster if is_ssl_{{ app.name }}
  {% endfor %}

  {% for app in ssl_apps %}
  {% for backend in app.backends %}
  backend {{ backend.name }}_cluster
      mode tcp

      # maximum SSL session ID length is 32 bytes.
      stick-table type binary len 32 size 30k expire 30m

      acl clienthello req_ssl_hello_type 1
      acl serverhello rep_ssl_hello_type 2

      # use tcp content accepts to detects ssl client and server hello.
      tcp-request inspect-delay 5s
      tcp-request content accept if clienthello

      # no timeout on response inspect delay by default.
      tcp-response content accept if serverhello

      stick on payload_lv(43,1) if clienthello

      # Learn on response if server hello.
      stick store-response payload_lv(43,1) if serverhello

      option ssl-hello-chk

      server {{ backend.name }} {{ backend.ip }}:{{ backend.port }} check

  {% endfor %}
  {% endfor %}
{% endif %}

frontend http_proxy
  bind 0.0.0.0:80

  mode    http
  option  httplog
  option  httpclose
  option  forwardfor

  {% for app in apps %}
  {% for domain in app.domains %}
  acl is_{{ app.name }} hdr(host) -i {{ domain }}
  {% endfor %}
  use_backend backend_{{ app.name }}_cluster if is_{{ app.name }}
  {% endfor %}

  {% for app in apps %}
  {% for backend in app.backends %}
  backend {{ backend.name }}_cluster
      mode    http
      server {{ backend.name }} {{ backend.ip }}:{{ backend.port }}
  {% endfor %}
  {% endfor %}
"""

from jinja2 import Template

logger = logging.getLogger('mcloud.plugin.haproxy')

class HaproxyConfig(object):

    def __init__(self, path, template=None):
        self.template = template
        self.path = path

    def dump(self, apps_list):

        template = self.template

        if not template:
            template = Template(HAPROXY_TPL)

        proxy_apps = []
        proxy_ssl_apps = []

        for app in apps_list:
            if not 'web_ip' in app or not app['web_ip']:
                continue

            domains = [app['fullname']]
            ssl_domains = []

            if app['public_urls']:
                for url in app['public_urls']:
                    if url.startswith('https://'):
                        ssl_domains.append(url[8:])
                    else:
                        domains.append(url)

            if ssl_domains:
                proxy_ssl_apps.append({
                    'name': app['fullname'],
                    'domains': ssl_domains,
                    'backends': [{'name': 'backend_ssl_%s' % app['fullname'], 'ip': app['web_ip'], 'port': 443}]
                })

            proxy_apps.append({
                'name': app['fullname'],
                'domains': domains,
                'backends': [{'name': 'backend_%s' % app['fullname'], 'ip': app['web_ip'], 'port': 80}]
            })

        log.msg('Writing haproxy config')

        with open('/etc/haproxy/haproxy.cfg', 'w') as f:
            f.write(template.render({'apps': proxy_apps, 'ssl_apps': proxy_ssl_apps}))

        os.system('service haproxy reload')


class HaproxyPlugin(Plugin):
    eb = inject.attr(EventBus)
    app_controller = inject.attr(ApplicationController)

    def __init__(self):
        super(HaproxyPlugin, self).__init__()

        self.eb.on('containers.updated', self.containers_updated)
        self.proxy_config = HaproxyConfig(path='/etc/haproxy/haproxy.cfg')

        logger.info('Haproxy plugin started')

        self.containers_updated()

    @inlineCallbacks
    def containers_updated(self, *args, **kwargs):
        logger.info('Containers updated: dumping haproxy config.')
        data = yield self.app_controller.list()
        self.proxy_config.dump(data)
