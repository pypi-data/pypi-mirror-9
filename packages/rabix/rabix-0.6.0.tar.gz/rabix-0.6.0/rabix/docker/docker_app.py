import os
import six
import shlex
import logging
import docker

from docker.errors import APIError
from six.moves.urllib.parse import urlparse

from rabix.common.models import FileConstructor
from rabix.cli.cli_app import Container
from rabix.docker.container import get_image
from rabix.common.errors import ResourceUnavailable


log = logging.getLogger(__name__)

DOCKER_DEFAULT_API_VERSION = "1.12"
DOCKER_DEFAULT_TIMEOUT = 60


def docker_client(docker_host=None,
                  api_version=DOCKER_DEFAULT_API_VERSION,
                  timeout=DOCKER_DEFAULT_TIMEOUT,
                  tls=None):

    docker_host = docker_host or os.getenv("DOCKER_HOST", None)
    tls = False if tls is None else os.getenv("DOCKER_TLS_VERIFY", "") != ""
    docker_cert_path = os.getenv("DOCKER_CERT_PATH", "")  # ???

    return docker.Client(docker_host, api_version, timeout, tls)


def make_config(**kwargs):
    keys = ['Hostname', 'Domainname', 'User', 'Memory', 'MemorySwap',
            'CpuShares', 'Cpuset', 'AttachStdin', 'AttachStdout',
            'AttachStderr', 'PortSpecs', 'ExposedPorts', 'Tty', 'OpenStdin',
            'StdinOnce', 'Env', 'Cmd', 'Image', 'Volumes', 'WorkingDir',
            'Entrypoint', 'NetworkDisabled', 'OnBuild']
    cfg = {
        'AttachStdin': False,
        'AttachStdout': False,
        'AttachStderr': False,
        'Tty': False,
        'Privileged': False,
        }
    cfg.update({k[0].upper() + k[1:]: v for k, v in six.iteritems(kwargs)})
    cfg = {k: v for k, v in six.iteritems(cfg) if k in keys}
    entrypoint = cfg.get("Entrypoint")
    if isinstance(entrypoint, six.string_types):
        cfg['Entrypoint'] = shlex.split(entrypoint)
    return cfg


class BindDict(dict):
    def items(self):
        ret = []
        for k, v in six.iteritems(super(BindDict, self)):
            ret.append((v, k))
        return ret


class DockerContainer(Container):

    def __init__(self, uri, image_id, dockr=None):
        super(DockerContainer, self).__init__()
        self.uri = uri.lstrip("docker://")\
            if uri and uri.startswith('docker:/') else uri

        self.image_id = image_id
        self.docker_client = dockr or docker_client()
        self.config = {}
        self.volumes = {}
        self.binds = {}

    def install(self, *args, **kwargs):
        try:
            get_image(self.docker_client,
                      image_id=self.image_id,
                      repo=self.uri)
        except APIError as e:
            if e.response.status_code == 404:
                log.info('Image %s not found:' % self.image_id)
                raise RuntimeError('Image %s not found:' % self.image_id)

    def prepare_paths(self, job):
        self.volumes, self.binds = self._volumes(job)

    def _volumes(self, job):
        remaped_job = job.inputs
        volumes = {}
        binds = {}

        input_values = remaped_job
        obj_inputs = job.app.inputs.io
        self._remap_obj(obj_inputs, input_values, volumes, binds, remaped_job)
        return volumes, BindDict(binds)

    def _remap_obj(self, inputs, input_values, volumes, binds, remaped_job,
                   parent=None):
        is_single = lambda i: i.constructor == FileConstructor and i.depth == 0
        is_list = lambda i: i.constructor == FileConstructor and i.depth == 1
        if inputs:
            single = filter(is_single, [i for i in inputs])
            lists = filter(is_list, [i for i in inputs])
            for inp in single:
                self._remap_single(inp, input_values, volumes, binds,
                                   remaped_job, parent)
            for inp in lists:
                self._remap_list(
                    inp, input_values, volumes, binds, remaped_job,
                    parent, inp.depth)

    def _remap_single(
            self, inp, input_values, volumes, binds, remaped_job, parent):
        if input_values.get(inp.id):
            if parent:
                docker_dir = '/' + '/'.join([parent, inp.id])
            else:
                docker_dir = '/' + inp.id
            dir_name, file_name = os.path.split(
                os.path.abspath(input_values[inp.id].path))
            volumes[docker_dir] = {}
            binds[docker_dir] = dir_name
            remaped_job[inp.id].path = '/'.join(
                [docker_dir, file_name])

    def _remap_list(
            self, inp, input_values, volumes, binds, remaped_job,
            parent, depth):
        if input_values.get(inp.id):

            for num, inv in enumerate(input_values[inp.id]):
                if parent:
                    docker_dir = '/' + '/'.join([parent, inp.id, str(num)])
                else:
                    docker_dir = '/' + '/'.join([inp.id, str(num)])
                dir_name, file_name = os.path.split(
                    os.path.abspath(inv.path))
                volumes[docker_dir] = {}
                binds[docker_dir] = dir_name
                remaped_job[inp.id][num].path = '/'.join(
                    [docker_dir, file_name])

    def set_config(self, *args, **kwargs):
        self.prepare_paths(kwargs.get('job'))
        user = kwargs.get('user', None) or ':'.join([str(os.getuid()),
                                                     str(os.getgid())])
        self.job_dir = kwargs.get('job_dir')
        self.volumes['/' + self.job_dir] = {}
        self.binds['/' + self.job_dir] = os.path.abspath(self.job_dir)
        self.stderr = kwargs.get('stderr') or 'out.err'
        cfg = {
            "Image": self.image_id,
            "User": user,
            "Volumes": self.volumes,
            "WorkingDir": self.job_dir
        }
        self.config = make_config(**cfg)

    def _start(self, cmd):
        self.config["Cmd"] = ['bash', '-c', cmd]
        try:
            self.container = self.docker_client.create_container_from_config(
                self.config)
        except APIError:
            raise RuntimeError('Failed to create Container')
        try:
            self.docker_client.start(container=self.container, binds=self.binds)
        except APIError:
            logging.error('Failed to run container %s' % self.container)
            raise RuntimeError('Unable to run container from image %s:'
                               % self.image_id)

    def run(self, cmd):  # should be run(self, cmd_line, job)
        self._start(cmd)
        self.get_stderr(file='/'.join([os.path.abspath(self.job_dir),
                                       self.stderr]))
        if not self.is_success():
            raise RuntimeError("err %s" % self.get_stderr())

    def remove(self, success_only=False):
        self.wait()
        if not success_only or self.is_success():
            self.docker_client.remove_container(self.container)
        return self

    def inspect(self):
        return self.docker_client.inspect_container(self.container)

    def is_running(self):
        return self.inspect()['State']['Running']

    def wait(self):
        if self.is_running():
            self.docker_client.wait(self.container)
        return self

    def is_success(self):
        return self.wait().inspect()['State']['ExitCode'] == 0

    def get_stdout(self, file=None):
        if file:
            f = open(file, 'w', buffering=1)
        if self.is_running():
            for out in self.docker_client.attach(self.container, stdout=True,
                                                 stderr=False, stream=True,
                                                 logs=True):
                if file:
                    f.write(out.rstrip() + '\n')
                else:
                    print(out.rstrip())
            if file:
                f.close()
        else:
            print(self.docker_client.logs(self.container))
        return self

    def get_stderr(self, file=None):
        if file:
            f = open(file, 'w')
            if self.is_running():
                for out in self.docker_client.attach(self.container,
                                                     stdout=False, stderr=True,
                                                     stream=True, logs=True):
                    if file:
                        f.write(str(out).rstrip() + '\n')
                    else:
                        print(out.rstrip())
            else:
                f.write(self.docker_client.logs(self.container,
                                                stdout=False, stderr=True))
            f.close()
        else:
            print(self.docker_client.logs(self.container))
        return self

    def to_dict(self, context=None):
        return {
            "@type": "Docker",
            "type": "docker",
            "uri": self.uri,
            "imageId": self.image_id
        }

    @classmethod
    def from_dict(cls, context, d):
        return cls(d.get('uri'), d.get('imageId'))
