import hashlib
import pickle
import os
import shutil

import requests

from hgross.crypt import encrypt
from hgross import racelog
from hgross.speedwise.util import recursive_glob, ensure_dir, path_leaf


__author__ = 'Henning Gross'
VERSION = '1.0.0'
_RACELOG_VERSION_HEADERS_KEY = 'RacelogVersion'
_SPEEDWISE_CLIENT_VERSION_HEADERS_KEY = 'SpeedwiseClientVersion'

class SpeedwiseClient():
    """
        The main client for speedwise (server node to the speedwise page).
        Sends data from server nodes to the speedwise system.
    """

    def __init__(self, speedwise_hostname, speedwise_port, server_id, server_shared_secret, protocol="http"):
        assert(racelog.VERSION == VERSION)
        self.speedwise_hostname = speedwise_hostname
        self.speedwise_port = int(speedwise_port)
        self.protocol = protocol
        self.server_id = server_id
        self.server_shared_secret = server_shared_secret
        self.headers = {
            _RACELOG_VERSION_HEADERS_KEY: racelog.VERSION,
            _SPEEDWISE_CLIENT_VERSION_HEADERS_KEY: VERSION
        }

    def _hash_data(self, content):
        "Hashes the data to send with the server_shared_secret"
        return hashlib.sha512(content + self.server_shared_secret).hexdigest()

    def retrieve_blacklist_txt(self, use_customized_blacklist=True):
        "Retrieves the blacklist from the speedwise server. If use_customized_blacklist is True, the customized ban list from speedwise.de for this server is merged into the global ban list."
        path = "court/blacklist.txt"
        if use_customized_blacklist:
            path = "%s?server_id=%s" % (path, str(self.server_id))
        url = u"%s://%s:%d/%s" % (self.protocol, self.speedwise_hostname, self.speedwise_port, path)
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                return None
            return response.content
        except Exception as e:
            return None

    def send_session(self, session):
        "Send a racelog session to speedwise"
        assert (isinstance(session, racelog.Session))
        # serialize and encrypt
        serialized = pickle.dumps(session)
        serialized = encrypt(self.server_shared_secret, serialized)
        hash = self._hash_data(serialized)
        path = "server_data/v%s/%s/%s/" % (racelog.VERSION, self.server_id, hash)
        url = u"%s://%s:%d/%s" % (self.protocol, self.speedwise_hostname, self.speedwise_port, path)
        try:
            response = requests.post(url, serialized, headers=self.headers)
            return response.status_code == 204
        except Exception as e:
            return False

    def send_keep_alive(self, server_guid):
        "Send a keep alive to speedwise for the given server instance guid"
        content = str(server_guid)
        hash = self._hash_data(content)
        path = "gameserver_keepalive/%s/%s/" % (self.server_id, hash)
        url = u"%s://%s:%d/%s" % (self.protocol, self.speedwise_hostname, self.speedwise_port, path)
        try:
            response = requests.post(url, content, headers=self.headers)
            return response.status_code == 200
        except Exception as e:
            return None

    def process_session_data(self, todo_folder, sent_folder):
        "Searches todo_folder for pickle files and sends them. Every successfully processed file will be moved to the sent folder."
        # TODO: be more cautios if something goes wrong (not stupidly resent) - some queue stuff maybe?
        files = recursive_glob(todo_folder, "*.pickle")
        ensure_dir(todo_folder)
        ensure_dir(sent_folder)
        for file in files:
            session = None
            basename = path_leaf(file)
            with open(file, "r") as f:
                session = pickle.load(f)
                f.close()
            send_result = self.send_session(session)
            if send_result:
                # move to sent_folder
                shutil.move(file, sent_folder + os.path.sep + basename)
            elif send_result is None:
                print (u"Could not send %s to server. Seems to be offline. Will send later ..." % basename)
                break
            else:
                print (u"Could not send %s to server. Server error!" % basename)
