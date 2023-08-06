import logging
import re
import inject
from mcloud.remote import ApiRpcServer
from mcloud.txdocker import IDockerClient, DockerConnectionFailed
from twisted.internet import defer
from twisted.internet.defer import inlineCallbacks, returnValue
import txredisapi
import os

logger = logging.getLogger('mcloud.application')

class NotInspectedYet(Exception):
    pass


class Service(object):

    NotInspectedYet = NotInspectedYet

    client = inject.attr(IDockerClient)

    dns_server = inject.attr('dns-server')
    settings = inject.attr('settings')
    dns_search_suffix = inject.attr('dns-search-suffix')
    redis = inject.attr(txredisapi.Connection)

    rpc_server = inject.attr(ApiRpcServer)

    def __init__(self, **kwargs):
        self.image_builder = None
        self.name = None
        self.app_name = None
        self.entrypoint = None
        self.workdir = None
        self.volumes = []
        self.volumes_from = None
        self.ports = None
        self.web_port = None
        self.ssl_port = None
        self.command = None
        self.env = None
        self.config = None
        self.status_message = ''
        self._inspect_data = None
        self._inspected = False
        self.wait = False

        self.cpu_usage = 0.0
        self.memory_usage = 0

        self.__dict__.update(kwargs)
        super(Service, self).__init__()



    def task_log(self, ticket_id, message):
        self.rpc_server.task_progress(message, ticket_id)

    def build_docker_config(self):
        pass


    @inlineCallbacks
    def inspect(self):
        self._inspected = True
        data = yield self.client.inspect(self.name)
        self._inspect_data = data

        try:
            metrics = yield self.redis.hget('metrics', self.name)
            if metrics:
                self.memory_usage, self.cpu_usage = metrics.split(';')
        except inject.InjectorException:
            pass

        defer.returnValue(self._inspect_data)

    def is_running(self):
        if not self.is_inspected():
            raise self.NotInspectedYet()
        try:
            return self.is_created() and self._inspect_data['State']['Running']
        except KeyError:
            return False

    @property
    def shortname(self):
        name_ = self.name
        if self.app_name and name_.endswith(self.app_name):
            name_ = name_[0:-len(self.app_name) - 1]
        return name_

    def ip(self):
        if not self.is_running():
            return None

        return self._inspect_data['NetworkSettings']['IPAddress']

    def image(self):
        if not self.is_created():
            return None

        return self._inspect_data['Image']

    def hosts_path(self):
        if not self.is_created():
            return None

        return self._inspect_data['HostsPath']

    def list_volumes(self):
        if not self.is_created():
            return None

        volumes_ = self._inspect_data['Volumes']

        internal_volumes = (
            '/var/run/mcloud',
            '/usr/bin/@me'
        )
        for iv in internal_volumes:
            if iv in volumes_:
                del volumes_[iv]

        return volumes_

    def public_ports(self):
        if not self.is_running():
            return None

        return self._inspect_data['NetworkSettings']['Ports']

    def attached_volumes(self):
        if not self.is_running():
            return None

        return self.list_volumes().keys()

    def started_at(self):
        if not self.is_running():
            return None

        return self._inspect_data['State']['StartedAt']

    def is_web(self):
        return not self.web_port is None

    def get_web_port(self):
        return self.web_port

    def is_ssl(self):
        return not self.ssl_port is None

    def get_ssl_port(self):
        return self.ssl_port

    def is_created(self):
        if not self.is_inspected():
            raise self.NotInspectedYet()

        return not self._inspect_data is None

    @inlineCallbacks
    def run(self, ticket_id, command, size=None):

        image_name = yield self.image_builder.build_image(ticket_id=ticket_id)

        config = yield self._generate_config(image_name, for_run=True)

        config['Cmd'] = command
        config['Tty'] = True
        config['AttachStdin'] = True
        config['AttachStdout'] = True
        config['OpenStdin'] = True

        name = '%s_pty_%s' % (self.name, ticket_id)

        yield self.client.create_container(config, name, ticket_id=ticket_id)

        run_config = {
            "Dns": [self.dns_server],
            "DnsSearch": '%s.%s' % (self.app_name, self.dns_search_suffix)
        }

        run_config['VolumesFrom'] = self.name

        if self.ports:
            run_config['PortBindings'] = dict([(port, [{}]) for port in self.ports])

        if self.volumes and len(self.volumes):
            run_config['Binds'] = ['%s:%s' % (x['local'], x['remote']) for x in self.volumes]

        yield self.client.start_container(name, ticket_id=ticket_id, config=run_config)

        if size:
            yield self.client.resize(name, width=size[1], height=size[0])
            yield self.client.attach(name, ticket_id)
        else:
            yield self.client.attach(name, ticket_id, skip_terminal=True)

    @inlineCallbacks
    def start(self, ticket_id):
        id_ = yield self.client.find_container_by_name(self.name)

        self.task_log(ticket_id, '[%s][%s] Starting service' % (ticket_id, self.name))
        self.task_log(ticket_id, '[%s][%s] Service resolve by name result: %s' % (ticket_id, self.name, id_))

        # container is not created yet
        if not id_:
            self.task_log(ticket_id, '[%s][%s] Service not created. Creating ...' % (ticket_id, self.name))
            yield self.create(ticket_id)
            id_ = yield self.client.find_container_by_name(self.name)

        current_config = yield self.inspect()
        image_id = current_config['Image']
        image_info = yield self.client.inspect_image(image_id)

        self.task_log(ticket_id, '[%s][%s] Starting service...' % (ticket_id, self.name))

        config = {
            "Dns": [self.dns_server],
            "DnsSearch": '%s.%s' % (self.app_name, self.dns_search_suffix)
        }

        if self.volumes_from:
            config['VolumesFrom'] = self.volumes_from

        if self.ports:
            config['PortBindings'] = dict([(port, [{}]) for port in self.ports])

        mounted_volumes = []
        config['Binds'] = []
        if self.volumes and len(self.volumes):
            for x in self.volumes:
                mounted_volumes.append(x['remote'])
                config['Binds'].append('%s:%s' % (x['local'], x['remote']))


        if image_info['ContainerConfig']['Volumes']:
            for vpath, vinfo in image_info['ContainerConfig']['Volumes'].items():

                if not vpath in mounted_volumes:
                    dir_ = os.path.expanduser('%s/volumes/%s/%s' % (self.settings.home_dir, self.name, re.sub('[^a-z0-9]+', '_', vpath)))

                    if self.settings.btrfs:
                        dir_ += '_btrfs'

                    if not os.path.exists(dir_):
                        if self.settings.btrfs:
                            os.system('btrfs subvolume create %s' % dir_)
                        else:
                            os.makedirs(dir_)

                    mounted_volumes.append(vpath)
                    config['Binds'].append('%s:%s' % (dir_, vpath))

        self.task_log(ticket_id, 'Startng container with config: %s' % config)

        #config['Binds'] = ["/home/alex/dev/mcloud/examples/static_site1/public:/var/www"]

        yield self.client.start_container(id_, ticket_id=ticket_id, config=config)

        # inspect and return result
        ret = yield self.inspect()

        defer.returnValue(ret)


    @inlineCallbacks
    def stop(self, ticket_id):

        id = yield self.client.find_container_by_name(self.name)

        yield self.client.stop_container(id, ticket_id=ticket_id)

        ret = yield self.inspect()
        defer.returnValue(ret)


    @inlineCallbacks
    def pause(self, ticket_id):

        id = yield self.client.find_container_by_name(self.name)

        yield self.client.pause_container(id, ticket_id=ticket_id)

        ret = yield self.inspect()
        defer.returnValue(ret)


    @inlineCallbacks
    def unpause(self, ticket_id):

        id = yield self.client.find_container_by_name(self.name)

        yield self.client.unpause_container(id, ticket_id=ticket_id)

        ret = yield self.inspect()
        defer.returnValue(ret)

    @inlineCallbacks
    def _generate_config(self, image_name, for_run=False):
        config = {
            "Image": image_name,
        }

        image_info = None
        # TODO: improve tests
        if hasattr(self.client, 'inspect_image'):
            image_info = yield self.client.inspect_image(image_name)

        vlist = yield self.redis.hgetall('vars')

        if self.env:
            vlist.update(self.env)

        if len(vlist) > 0:
            config['Env'] = ['%s=%s' % x for x in vlist.items()]

        if self.ports:
            config['ExposedPorts'] = dict([(port, {}) for port in self.ports])


        if self.entrypoint:
            config['Entrypoint'] = self.entrypoint

        if self.workdir:
            config['WorkingDir'] = self.workdir

        if not for_run:
            config['Hostname'] = self.name

            if self.command:
                config['Cmd'] = self.command.split(' ')

            if self.volumes and len(self.volumes):
                config['Volumes'] = dict([
                    (x['remote'], {}) for x in self.volumes
                ])

            if image_info and image_info['ContainerConfig']['Volumes']:
                for vpath, vinfo in image_info['ContainerConfig']['Volumes'].items():
                    config['Volumes'][vpath] = {}

        defer.returnValue(config)


    @inlineCallbacks
    def create(self, ticket_id):

        image_name = yield self.image_builder.build_image(ticket_id=ticket_id)

        config = yield self._generate_config(image_name)
        yield self.client.create_container(config, self.name, ticket_id=ticket_id)

        ret = yield self.inspect()
        defer.returnValue(ret)

    @inlineCallbacks
    def destroy(self, ticket_id):
        id_ = yield self.client.find_container_by_name(self.name)
        yield self.client.remove_container(id_, ticket_id=ticket_id)

        ret = yield self.inspect()
        defer.returnValue(ret)

    def is_inspected(self):
        return self._inspected




