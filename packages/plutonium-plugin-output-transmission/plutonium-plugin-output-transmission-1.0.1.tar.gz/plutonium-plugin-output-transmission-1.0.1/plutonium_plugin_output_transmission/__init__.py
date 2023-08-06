import json
import base64
import transmissionrpc

from plutonium.plugins.plugin import OutputPluginBase
from plutonium.modules.tools import xml_element_to_storage, Storage
from plutonium.modules.logger import get_logger

logger = get_logger(__name__, 'plutonium')

from plutonium.modules.orm.types import StructField as Field

class TransmissionOutputPlugin(OutputPluginBase):

    def __init__(self, plutonium):
        self.url_loader = plutonium.url_loader
        self.clients = {}

    def get_required_params_struct(self):
        """
        return dict(
            host = str,
            port = int,
            path = str,
            ssl = bool,
            auth = dict(
                enabled = bool,
                username = str,
                password = str
            )
        )
        """
        return [
            Field('host', str, required = True),
            Field('port', int, default = 9091, required = True),
            Field('path', str, default = '/transmission/rpc', required = True),
            Field('ssl', bool, default = False),
            Field('auth', nodes = [
                Field('enabled', bool, default = False),
                Field('username', str),
                Field('password', str)
            ])
        ]

    def get_client(self, output):
        if output.id not in self.clients:
            params = output.params
            logger.info("Create transmission client to %s" % params)
            self.clients[output.id] = transmissionrpc.Client('http://%(host)s:%(port)d%(path)s' % params)

        return self.clients[output.id]

    def send(self, torrent):
        try:

            params = torrent.feed.output.params

            if params is None:
                return False

            # download the torrent file
            torrent_content = self.url_loader.load(torrent.link).content

            client = self.get_client(torrent.feed.output)

            arguments = {
                'download-dir': torrent.fetch_download_dir(),
                'paused': False
            }

            # the result is transmissionrpc.Torrent instance
            result = client.add_torrent(base64.b64encode(torrent_content), **arguments)

            logger.debug("Torrent has been successfully added for the remote transmission service: %s, with %s" % (result, arguments))
            return True

        except Exception as e:
            logger.error("Exception occurred during torrent processing in transmission output plugin: %s" % e)
            return False

    def start(self):
        pass

    def stop(self):
        pass

    def reload(self):
        pass
