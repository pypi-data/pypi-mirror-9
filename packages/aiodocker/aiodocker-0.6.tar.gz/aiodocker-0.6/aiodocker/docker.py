import io
import os
import base64
import urllib
import aiohttp
import asyncio
import hashlib
import tarfile
import json
import datetime as dt
from aiohttp import websocket

from aiodocker.channel import Channel
from aiodocker.utils import identical


class Docker:
    def __init__(self, url="/run/docker.sock"):
        self.url = url
        self.events = DockerEvents(self)
        self.containers = DockerContainers(self)
        self.connector = aiohttp.connector.UnixConnector(url)

    @asyncio.coroutine
    def pull(self, image):
        url = self._endpoint("images/create", fromImage=image)

        response = yield from aiohttp.request(
            'POST', url,
            connector=self.connector,
            headers={"content-type": "application/json",},
        )

        while True:
            msg = yield from response.content.readany()
            if msg == b'':
                break
            # print(msg)
        return

    def _endpoint(self, path, **kwargs):
        string = "/".join([self.url, path])
        string = path
        if kwargs:
            string += "?" + urllib.parse.urlencode(kwargs)
        string = "http://fnord/%s" % (string)
        return string

    def _query(self, path, method='GET', params=None,
               data=None, headers=None, **kwargs):
        url = self._endpoint(path, **kwargs)
        response = yield from aiohttp.request(
            method, url,
            connector=self.connector,
            params=params, headers=headers, data=data)

        if (response.status // 100) in [4, 5]:
            what = yield from response.read()
            response.close()
            raise ValueError("Got a failure from the server: '%s'" % (
                what.decode('utf-8').strip()
            ))

        if 'json' in response.headers.get("Content-Type", ""):
            try:
                data = yield from response.json(encoding='utf-8')
            except ValueError as e:
                raise
            return data

        if 'application/x-tar' in response.headers.get("Content-Type", ""):
            what = yield from response.read()
            return tarfile.open(mode='r', fileobj=io.BytesIO(what))

        try:
            data = yield from response.content.read()  # XXX: Correct?
        except ValueError as e:
            print("Server said", chunk)
            raise

        response.close()
        return data


class DockerContainers:
    def __init__(self, docker):
        self.docker = docker

    @asyncio.coroutine
    def list(self, **kwargs):
        data = yield from self.docker._query(
            "containers/json",
            method='GET',
            **kwargs
        )
        return [DockerContainer(self.docker, **x) for x in data]

    @asyncio.coroutine
    def create_or_replace(self, name, config):
        container = None

        try:
            container = yield from self.get(name)
            if not identical(config, container._container):
                running = container._container.get(
                    "State", {}).get("Running", False)
                if running:
                    yield from container.stop()
                yield from container.delete()
                container = None
        except ValueError:
            pass

        if container is None:
            container = yield from self.create(config, name=name)

        return container

    @asyncio.coroutine
    def create(self, config, name=None):
        url = "containers/create"

        config = json.dumps(config, sort_keys=True, indent=4).encode('utf-8')
        kwargs = {}
        if name:
            kwargs['name'] = name
        data = yield from self.docker._query(
            url,
            method='POST',
            headers={"content-type": "application/json",},
            data=config,
            **kwargs
        )
        return DockerContainer(self.docker, id=data['Id'])

    @asyncio.coroutine
    def get(self, container, **kwargs):
        data = yield from self.docker._query(
            "containers/{}/json".format(container),
            method='GET',
            **kwargs
        )
        return DockerContainer(self.docker, **data)


class DockerContainer:
    def __init__(self, docker, **kwargs):
        self.docker = docker
        self._container = kwargs
        self._id = self._container.get("id", self._container.get(
            "ID", self._container.get("Id")))
        self.logs = DockerLog(docker, self)

    @asyncio.coroutine
    def log(self, stdout=False, stderr=False, **kwargs):
        if stdout is False and stderr is False:
            raise TypeError("Need one of stdout or stderr")

        data = yield from self.docker._query(
            "containers/{}/logs".format(self._id),
            method='GET',
            params={
                "stdout": stdout,
                "stderr": stderr,
                "follow": False,
            }
        )
        return data

    @asyncio.coroutine
    def copy(self, resource, **kwargs):
        request = json.dumps({
            "Resource": resource,
        }, sort_keys=True, indent=4).encode('utf-8')
        data = yield from self.docker._query(
            "containers/{}/copy".format(self._id),
            method='POST',
            data=request,
            headers={"content-type": "application/json",},
            **kwargs
        )
        return data

    @asyncio.coroutine
    def show(self, **kwargs):
        data = yield from self.docker._query(
            "containers/{}/json".format(self._id),
            method='GET',
            **kwargs
        )
        self._container = data
        return data

    @asyncio.coroutine
    def stop(self, **kwargs):
        data = yield from self.docker._query(
            "containers/{}/stop".format(self._id),
            method='POST',
            **kwargs
        )
        return data

    @asyncio.coroutine
    def start(self, config, **kwargs):
        config = json.dumps(config, sort_keys=True, indent=4).encode('utf-8')
        data = yield from self.docker._query(
            "containers/{}/start".format(self._id),
            method='POST',
            headers={"content-type": "application/json",},
            data=config,
            **kwargs
        )
        return data

    @asyncio.coroutine
    def kill(self, **kwargs):
        data = yield from self.docker._query(
            "containers/{}/kill".format(self._id),
            method='POST',
            **kwargs
        )
        return data

    @asyncio.coroutine
    def wait(self, **kwargs):
        data = yield from self.docker._query(
            "containers/{}/wait".format(self._id),
            method='POST',
            **kwargs
        )
        return data

    @asyncio.coroutine
    def delete(self, **kwargs):
        data = yield from self.docker._query(
            "containers/{}".format(self._id),
            method='DELETE',
            **kwargs
        )
        return data


class DockerEvents:
    def __init__(self, docker):
        self.running = False
        self.docker = docker
        self.channel = Channel()

    def listen(self):
        return self.channel.listen()

    def saferun(self):
        if self.running:
            return
        self.running = True
        asyncio.async(self.run())

    @asyncio.coroutine
    def run(self):
        self.running = True
        containers = self.docker.containers
        response = yield from aiohttp.request(
            'GET',
            self.docker._endpoint('events'),
            connector=self.docker.connector,
        )

        while True:
            chunk = yield from response.content.readany()
            # XXX: WTF. WTF WTF WTF. 
            # WHY AM I NOT GETTING A RETURN ON .READLINE()?! WHY NO NEWLINE
            # https://github.com/dotcloud/docker/pull/4276 ADDED THEM
            if chunk == b'':
                break
            data = json.loads(chunk.decode('utf-8'))

            if 'time' in data:
                data['time'] = dt.datetime.fromtimestamp(data['time'])

            if 'id' in data and data['status'] in [
                "start", "create",
            ]:
                data['container'] = yield from containers.get(data['id'])

            asyncio.async(self.channel.put(data))
        response.close()
        self.running = False


class DockerLog:
    def __init__(self, docker, container):
        self.docker = docker
        self.channel = Channel()
        self.container = container
        self.running = False

    def listen(self):
        return self.channel.listen()

    def saferun(self):
        if self.running:
            return
        self.running = True
        asyncio.async(self.run())

    @asyncio.coroutine
    def run(self):
        self.running = True
        containers = self.docker.containers
        url = self.docker._endpoint(
            'containers/{id}/logs'.format(id=self.container._id),
            follow=True,
            stdout=True,
            stderr=True,
        )
        response = yield from aiohttp.request(
            'GET', url, connector=self.docker.connector)

        while True:
            msg = yield from response.content.readline()
            asyncio.async(self.channel.put(msg))
            if msg == b'':
                break

        self.running = False
