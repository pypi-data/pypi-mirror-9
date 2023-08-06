from ConfigParser import SafeConfigParser, ConfigParser
import base64
import json
import os
import StringIO

__author__ = 'Henning Gross'

def removeSpacesFromIniFile(filePath):
    "Corrects some problems with ac's ini parser"
    content = list()
    with open(filePath, "r") as inputfile:
        for line in inputfile:
            newLine = line.replace(" = ", "=", 1)
            content.append(newLine)
        inputfile.close()
    content = "".join(content)
    with open(filePath, "w") as outputfile:
        outputfile.write(content)
        outputfile.close()

class ACDedicatedServerConfig():
    "Abstracts the contents of the presets folder creatable with the ACServerLauncher.exe (the two ini files)"
    def __init__(self, presetFolderPath):
        "presetFolderPath --- the preset folder to use (containing entry_list.ini and server_cfg.ini"
        self.presetFolderPath = presetFolderPath
        self._validateFolderPath()
        self.preset_name = os.path.basename(os.path.abspath(presetFolderPath))
        self._parseServerConfig()
        self._parseEntryList()

    def _validateFolderPath(self):
        folderExists = os.path.isdir(self.presetFolderPath)
        configFilesExist = os.path.exists(self.presetFolderPath + os.path.sep + "server_cfg.ini") and os.path.exists(self.presetFolderPath + os.path.sep + "entry_list.ini")
        if not folderExists:
            raise BaseException("presetFolderPath (%s) does not exist" % self.presetFolderPath)
        if not configFilesExist:
            raise BaseException("Either the server_cfg.ini or entry_list.ini is missing in folder %s" % self.presetFolderPath)

    def _parseEntryList(self):
        f = open(self.presetFolderPath + os.path.sep + "entry_list.ini", "r")
        self.entry_list = ConfigParser()
        self.entry_list.optionxform = str # preserves case
        self.entry_list.readfp(f)
        f.close()
        #print (self.entry_list.sections())

    def _parseServerConfig(self):
        f = open(self.presetFolderPath + os.path.sep + "server_cfg.ini", "r")
        self.server_cfg = ConfigParser()
        self.server_cfg.optionxform = str # preserves case
        self.server_cfg.readfp(f)
        f.close()
        #print (self.server_cfg.sections())

    def exportConfig(self, folderPath):
        "Writes the entry_list.ini and server_cfg.ini to the given folder"
        entry_list_path = folderPath + os.path.sep + "entry_list.ini"
        server_cfg_path = folderPath + os.path.sep + "server_cfg.ini"
        entry_list = open(entry_list_path, "w")
        server_cfg = open(server_cfg_path, "w")
        self.entry_list.write(entry_list)
        self.server_cfg.write(server_cfg)
        entry_list.close()
        server_cfg.close()
        removeSpacesFromIniFile(entry_list_path)
        removeSpacesFromIniFile(server_cfg_path)

    def to_json(self):
        "Serializes a preset to json format"
        entry_list_buffer = StringIO.StringIO()
        server_cfg_buffer = StringIO.StringIO()
        self.entry_list.write(entry_list_buffer)
        self.server_cfg.write(server_cfg_buffer)
        entry_list64 = base64.b64encode(entry_list_buffer.getvalue())
        entry_list_buffer.close()
        server_cfg64 = base64.b64encode(server_cfg_buffer.getvalue())
        server_cfg_buffer.close()
        return json.dumps({
            "preset_name": self.preset_name,
            "entry_list": entry_list64,
            "server_cfg": server_cfg64
        })



class ACServerWrapperConfig:
    def __init__(self, config_file_path):
        # Read config file
        cfg = SafeConfigParser()
        f = open(config_file_path)
        cfg.readfp(f)
        f.close()
        self.DEDICATED_SERVER_BASE_DIRECTORY = cfg.get("Paths", "DedicatedServerBaseDirectory")
        self.DEDICATED_SERVER_PRESETS_DIRECTORY = cfg.get("Paths", "DedicatedServerPresetsFolder")
        self.DEDICATED_SERVER_WORKSPACES_DIRECTORY = cfg.get("Paths", "DedicatedServerWorkspacesFolder")
        self.speedwise_server_id = cfg.get("Speedwise", "SpeedwiseServerId")
        self.speedwise_server_secret = cfg.get("Speedwise", "SpeedwiseServerSecret")
        self.speedwise_server_hostname = cfg.get("Speedwise", "SpeedwiseHost")
        self.speedwise_server_port = cfg.get("Speedwise", "SpeedwisePort")
        self.merge_blacklist = cfg.get("Blacklist", "MergeBlacklist") if cfg.has_section("Blacklist") and cfg.has_option("Blacklist", "MergeBlacklist") else None
