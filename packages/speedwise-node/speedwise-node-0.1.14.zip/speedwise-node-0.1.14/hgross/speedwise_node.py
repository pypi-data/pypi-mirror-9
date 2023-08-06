import argparse
import base64
import codecs
import json
import sys
import os
import time
import cherrypy
import requests
from threading import Lock

from hgross.crypt import encrypt, decrypt
from hgross.ac import ACServerWrapper
from hgross.ac.ACServerWrapper import ACServerWrapperConfig, PresetDoesNotExist


__author__ = 'Henning Gross'

__VERSION__ = '1.1.0' # version for the speedwise node interface and client (note: racelog has it's own versions)
_VERSION_HEADERS_KEY = "SpeedwiseServerNodeVersion"

class SecurityException(Exception): pass

def decrypt_message(secret, msg, t):
    "Decrypts message with time t"
    decrypted = decrypt(secret, msg)
    t = str(t)
    l = len(t)
    extracted_t, decrypted_msg = decrypted[:l], decrypted[l:]
    if not str(extracted_t) == t:
        raise SecurityException("Decryption failed")
    return decrypted_msg

def encrypt_message(secret, msg):
    "Returns (t, encrypted_message)"
    t = str(time.time())
    return t, encrypt(secret, t+msg)


class SpeedwiseNodeClient():
    "Client for SpeedwiseNode (start, presets, ...)"

    class WrongVersionException(Exception): pass

    def __init__(self, server_host, server_port, server_id, shared_secret, timeout=10):
        self.server_host = server_host
        self.server_port = int(server_port)
        self.server_id = server_id
        self.shared_secret = shared_secret
        self.base_url = "http://%s:%d/" % (self.server_host, self.server_port)
        self.timeout = timeout # the timeout to use for every request
        self.headers = {
            _VERSION_HEADERS_KEY: __VERSION__
        }

    def _check_version(self, response):
        assert isinstance(response, requests.Response)
        if response.headers.get(_VERSION_HEADERS_KEY) != __VERSION__:
            raise SpeedwiseNodeClient.WrongVersionException()
        return response

    def start_preset(self, preset_name):
        "Instructs the node to start the given preset"
        msg = {"preset_id": preset_name}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "start?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        return response.content

    def get_presets(self):
        "Retrieves the list of presets from the node"
        msg = {}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "presets?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        return json.loads(response.content)["presets"]

    def get_server_list(self):
        'Returns a list of servers. Tuple: ("GUID", "Running", "WorkingDirectory")'
        msg = {}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "get_server_list?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        return json.loads(response.content)["server_list"]

    def update_blacklist(self):
        'Instructs the node to update the blacklist - True if the command was successful.'
        msg = {}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "update_blacklist?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        return json.loads(response.content)["result"]

    def stop_server(self, server_guid):
        "Stops a server with a given guid"
        msg = {"server_guid": server_guid}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "stop_server?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        return json.loads(response.content)["result"]

    def stop_all_servers(self):
        "Stops all servers"
        msg = {}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "stop_all_servers?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        return True

    def clean_workspace(self):
        "Cleans the workspace of not running servers"
        msg = {}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "clean_workspace?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        return True

    def get_preset_files(self, preset_name):
        "Stops a server with a given guid"
        msg = {"preset_name": preset_name}
        msg = json.dumps(msg)
        t, data = encrypt_message(self.shared_secret, msg)
        url = self.base_url + "get_preset_files?t=%s" % t
        response = requests.post(url, data, timeout=self.timeout, headers=self.headers)
        self._check_version(response)
        if not response.status_code == 200:
            return None
        data = json.loads(response.content)
        # decode b64
        data["entry_list"] = base64.b64decode(data["entry_list"])
        data["server_cfg"] = base64.b64decode(data["server_cfg"])
        return data


_SERVERS_LOCK = Lock()

class SpeedwiseNode():
    "The web interface"
    def __init__(self, wrapperConfig):
        assert isinstance(wrapperConfig, ACServerWrapperConfig)
        self.server_id = wrapperConfig.speedwise_server_id
        self.shared_secret = wrapperConfig.speedwise_server_secret
        self.wrapperConfig = wrapperConfig

    def _append_headers(self):
        cherrypy.response.headers[_VERSION_HEADERS_KEY] = __VERSION__

    def _check_version(self):
        if not cherrypy.request.headers.has_key(_VERSION_HEADERS_KEY):
            raise cherrypy.HTTPError(400, 'Bad Request: Wrong version. Update your speedwise-server-node library (pip install --upgrade speedwise-server-node)')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def start(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        msg = json.loads(msg)
        preset_id = msg["preset_id"]

        with _SERVERS_LOCK:
            presets = ACServerWrapper.getPresets(self.wrapperConfig)
            if not preset_id in presets:
                cherrypy.response.status = 404
                return "Preset not found. Available presets are %s" % (str(presets), )
            server = ACServerWrapper.start_server_from_preset(preset_id, self.wrapperConfig)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def presets(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        with _SERVERS_LOCK:
            presets = ACServerWrapper.getPresets(self.wrapperConfig)
            return json.dumps({"presets": presets})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def get_server_list(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        with _SERVERS_LOCK:
            server_list = ACServerWrapper.getStatusForServers(self.wrapperConfig)
            return json.dumps({"server_list": server_list})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def update_blacklist(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        with _SERVERS_LOCK:
            result = ACServerWrapper.updateBlacklist(self.wrapperConfig)
            return json.dumps({"result": result})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def stop_server(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        msg = json.loads(msg)
        server_guid = msg["server_guid"]

        with _SERVERS_LOCK:
            result = ACServerWrapper.stop_server(self.wrapperConfig, server_guid)
            return json.dumps({"result": result})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def stop_all_servers(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        with _SERVERS_LOCK:
            result = ACServerWrapper.stop_all_servers(self.wrapperConfig)
        return ""

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def clean_workspace(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        with _SERVERS_LOCK:
            result = ACServerWrapper.clean_workspace(self.wrapperConfig)
        return ""

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def get_preset_files(self, t):
        self._append_headers()
        self._check_version()
        data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        msg = decrypt_message(self.shared_secret, data, t)
        msg = json.loads(msg)
        preset_name = msg["preset_name"]
        with _SERVERS_LOCK:
            # get config
            cfg = ACServerWrapper.getPresetConfigByName(self.wrapperConfig, preset_name)
            if not cfg:
                raise cherrypy.HTTPError(404)
            out = cfg.to_json()
            return out

def main_func():
    "The main"
    sys.stdout = codecs.getwriter("utf8")(sys.stdout);
    argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Start a speedwise-server-node instance.")
    argParser.add_argument('--config-file', default="speedwise.ini", help='The assetto corsa wrapper\'s config file path. If not specified, speedwise.ini in the current directory will be used (must exist.')
    argParser.add_argument("--preset", type=str, help="If given, this preset will be autostarted (if valid preset name)")
    args = argParser.parse_args()

    # load config
    if not os.path.isfile(args.config_file):
        print (u"Config not found! Sign in to speedwise (http://speedwise.de/gameserver_admins/gameservers/) to get your shared secret and server id and follow the instructions.\n\n Use -h for help.")
        sys.exit(1)
    wrapperConfig = ACServerWrapperConfig(args.config_file)
    node = SpeedwiseNode(wrapperConfig)

    # cherrypy config and startup
    cherrypy.config.update({
        'environment': 'production',
        'log.error_file': 'speedwise_node.log'
    })
    cherrypy.server.socket_host =  '0.0.0.0'
    cherrypy.server.socket_port = 9055 # TODO: make configurable
    cherrypy.tree.mount(node)
    cherrypy.engine.start()

    # Example code for NodeClient usage:
    # client = SpeedwiseNodeClient("127.0.0.1", 9055, wrapperConfig.speedwise_server_id, wrapperConfig.speedwise_server_secret, timeout=20)
    # print client.update_blacklist()
    # presets = client.get_presets()
    # print presets
    # print client.start_preset(presets[0])
    # print client.start_preset(presets[1])
    # servers = client.get_server_list()
    # print servers
    # running_servers = [x for x in servers if x[1] == True]
    # print running_servers
    # for guid, _,_,_  in running_servers:
    #     print client.stop_server(guid)
    # print client.clean_workspace()

    if args.preset:
        try:
            ACServerWrapper.start_server_from_preset(args.preset, wrapperConfig)
        except PresetDoesNotExist:
            print (u"Couldn't autostart the preset %s. It does not exist in the presets folder." % args.preset)

    cherrypy.engine.block()


if __name__ == '__main__':
    main_func()
