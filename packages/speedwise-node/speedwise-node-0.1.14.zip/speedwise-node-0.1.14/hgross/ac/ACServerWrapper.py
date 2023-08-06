import glob
import signal
import os
import argparse
import shutil
import sys
import codecs

import psutil

from hgross.ac.ac_server import ACDedicatedServer, SERVER_WORKING_DIR_FILENAME_PREFIX, SERVER_PIDFILE_NAME, SERVER_PRESET_INDICATOR_NAME, DEDICATED_SERVER_BINARY_FILENAME
from hgross.ac.common import ACDedicatedServerConfig, ACServerWrapperConfig
from hgross.speedwise.speedwise_client import SpeedwiseClient

__author__ = 'Henning Gross'

def getPresets(wrapperConfig):
    "Returns a list of all subdirectories in the DEDICATED_SERVER_PRESETS_DIRECTORY directory - which are the presets available"
    l = [x[1] for x in os.walk(wrapperConfig.DEDICATED_SERVER_PRESETS_DIRECTORY) if x[0] == wrapperConfig.DEDICATED_SERVER_PRESETS_DIRECTORY]
    return [item for sublist in l for item in sublist] # flatten

def getPresetConfigByName(wrapperConfig, preset_name):
    "Returns the given present's config object by it's name - returns None if not found"
    for preset in getPresets(wrapperConfig):
        if preset == preset_name:
            folder = wrapperConfig.DEDICATED_SERVER_PRESETS_DIRECTORY + os.path.sep + preset_name
            cfg = ACDedicatedServerConfig(folder)
            return cfg
    return None

def getStatusForServers(wrapperConfig):
    "Returns a list of tuples where the form of each tuple corresponds to (server_guid (String), isRunning (Bool), WorkingDirectoryPath (String), Preset name (String))"
    try:
        # append preset name
        def get_preset_name(working_dir):
            with open(working_dir + os.path.sep + SERVER_PRESET_INDICATOR_NAME, "r") as preset_name_file:
                preset_name = str(preset_name_file.read())
                preset_name_file.close()
            return preset_name
        def is_running(working_dir):
            "checks whether the server is running by it's PID file"
            guid = working_dir.replace(wrapperConfig.DEDICATED_SERVER_WORKSPACES_DIRECTORY + os.path.sep + SERVER_WORKING_DIR_FILENAME_PREFIX, "")
            pid_file_path = working_dir + os.path.sep + SERVER_PIDFILE_NAME
            if not os.path.exists(pid_file_path):
                return False
            with open(pid_file_path) as pid_file:
                pid = pid_file.read()
                pid_file.close()
            if not pid:
                os.unlink(pid_file_path) # remove pid file
                return False

            # check if is a process and actually running
            try:
                p = psutil.Process(int(pid))
                is_really_running = DEDICATED_SERVER_BINARY_FILENAME in p.exe() and guid in p.exe() and p.cwd() == working_dir
                if not is_really_running:
                    os.unlink(pid_file_path) # remove pid file
                return is_really_running
            except psutil.NoSuchProcess:
                os.unlink(pid_file_path) # remove pid file
                return False


        servers = [(working_dir.replace(wrapperConfig.DEDICATED_SERVER_WORKSPACES_DIRECTORY + os.path.sep + SERVER_WORKING_DIR_FILENAME_PREFIX, ""), is_running(working_dir), working_dir, get_preset_name(working_dir)) for working_dir in glob.glob(wrapperConfig.DEDICATED_SERVER_WORKSPACES_DIRECTORY + os.path.sep + SERVER_WORKING_DIR_FILENAME_PREFIX + "*")]
        return servers
    except Exception as e:
        print e
        return []

def clean_workspace(wrapperConfig):
    "Removes all working directories of servers that are not running"
    statuses = getStatusForServers(wrapperConfig)
    print ("Removing all working directories of not running servers ...")
    for guid, running, workingDirPath, preset in statuses:
        if not running:
            print ("Removing working directory for server %s (%s)" % (guid, workingDirPath))
            shutil.rmtree(workingDirPath)
        else:
            print ("Server %s (%s) is running - not touching working directory." % (guid, workingDirPath))
    print ("Done.")

def stop_server(wrapperConfig, server_guid):
    "Stops the server with the specified guid - if running. Returns True if a sigterm was sent to the server process"
    status_list = getStatusForServers(wrapperConfig)
    server = None
    for server_tuple in status_list:
        guid = server_tuple[0]
        is_running = server_tuple[2]
        if guid == server_guid:
            server = server_tuple
            if not is_running:
                return True # not running - nothing to do

    if not server:
        print (u"No server with guid %s was found." % server_guid)
        return False
    working_dir = server[2]
    pid = None
    with open(working_dir + os.path.sep + SERVER_PIDFILE_NAME, "r") as pid_file:
        pid = pid_file.read()
        pid_file.close()
    if not pid:
        print (u"ERROR: could not get pid from pid file")
        return False
    # TODO: ensure pid is running - if not remove pidfile
    # kill pid
    print (u"Stopping server %s (PID: %s)" % (server_guid, pid))
    os.kill(int(pid), signal.SIGTERM)
    return True

def stop_all_servers(wrapperConfig):
    print (u"Stopping all servers ...")
    for guid, is_running, _, _  in getStatusForServers(wrapperConfig):
        if not is_running:
            continue
        result = stop_server(wrapperConfig, guid)
        print (u"Server %s %s" % (guid, ("stopped" if result else "not stopped")))

def updateBlacklist(wrapperConfig):
    "Retrieves the blacklist from the server and write it to the ACServer base directory. True if successful, False otherwise"
    merge_file = None
    if wrapperConfig.merge_blacklist and os.path.isfile(wrapperConfig.merge_blacklist):
        merge_file = wrapperConfig.merge_blacklist

    client = SpeedwiseClient(wrapperConfig.speedwise_server_hostname, wrapperConfig.speedwise_server_port, wrapperConfig.speedwise_server_id, wrapperConfig.speedwise_server_secret)
    contents = client.retrieve_blacklist_txt(use_customized_blacklist=True)
    if contents:
        print (u"Received blacklist from speedwise.")
        with open(wrapperConfig.DEDICATED_SERVER_BASE_DIRECTORY + os.path.sep + "blacklist.txt", "w") as blacklist_file:
            blacklist_file.write(contents)
            print (u"Updated blacklist.txt - %d entries." % len([x for x in contents.split("\n") if len(x) >= 17]))
            if merge_file:
                print (u"Merging contents of %s into received blacklist ..." % merge_file)
                with open(merge_file) as merge_fd:
                    i = 0
                    for line in merge_fd:
                        if i==0:
                            blacklist_file.write("\n")
                        blacklist_file.write(line)
                        i = i + 1
                    print (u"Merged %d entries into file" % i)
                    merge_fd.close()
            blacklist_file.close()
        return True

    else:
        print (u"Failed to retrieve blacklist. Check your internet connection.")
        return False


class PresetDoesNotExist (BaseException): pass

def start_server_from_preset(preset_name, wrapperConfig):
    "Starts a server based on the preset name. Raises PresetDoesNotExist, if preset not found."
    presets = getPresets(wrapperConfig)
    if not preset_name in presets:
        raise PresetDoesNotExist()
    presetFolderPath = wrapperConfig.DEDICATED_SERVER_PRESETS_DIRECTORY + os.path.sep + preset_name
    serverConfig = ACDedicatedServerConfig(presetFolderPath)
    server = ACDedicatedServer(serverConfig, wrapperConfig)
    server.start_server()
    return server

def main_func():
    "The main"
    sys.stdout = codecs.getwriter("utf8")(sys.stdout);
    COMMANDS = {"presets": "Lists all presets available for server creation",
                "start": "Starts a server with the given preset (--preset ...)",
                "stop": "Stops a server with the given guid (--guid...)",
                "stop_all": "Stops all running servers",
                "list": "Lists all servers in the working directory.",
                "clean": "Removes all working directories that are not used at the moment.",
                "update-blacklist": "Updates the blacklist.txt.",
                "config": "Shows the path of the config file"}

    argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Start a Assetto Corsa dedicated server instance", epilog="Descriptions for the command parameter options:\n\n%s" % ("\n".join(["%20s  %s" % t for t in COMMANDS.iteritems()])))
    argParser.add_argument("command", type=str, help="The command to execute", choices=COMMANDS.keys())
    argParser.add_argument("--preset", type=str, help="Folder name of the preset to use (creatable by the ACServerLauncher.exe)")
    argParser.add_argument("--guid", type=str, help="Server GUID (needed for the stop command)")
    argParser.add_argument('--config-file', default="speedwise.ini", help='This wrapper\'s config file path.')
    args = argParser.parse_args()
    command = args.command

    if not os.path.isfile(args.config_file):
        print (u"Error: Config file does not exist (%s).\nUse --config-file path/to/your/speedwise.ini to specify the correct path." % args.config_file)
        sys.exit(1)

    wrapperConfig = ACServerWrapperConfig(args.config_file)

    if command == "start":
        if not args.preset and len(getPresets(wrapperConfig)) == 0:
            raise BaseException("No preset specified")
        elif not args.preset and len(getPresets(wrapperConfig)) > 0:
            args.preset = getPresets(wrapperConfig)[0] # take first
            print ("WARNING: No preset defined with start command, defaulting to first (%s)" % args.preset)
        if not args.preset in getPresets(wrapperConfig):
            raise BaseException("This preset does not exist (%s). Available presets: %s" % (args.preset, "No presets available" if getPresets() == 0 else ", ".join(getPresets())))
        # finally create instance and start
        server = start_server_from_preset(args.preset, wrapperConfig)
    elif command == "presets":
        presets = getPresets(wrapperConfig)
        presetHeader = "Preset names"
        longestPresetLength = max(map(lambda x:len(x), presets + [presetHeader]))
        table_rows = [("%"+str(longestPresetLength)+"s | %s") % (preset, wrapperConfig.DEDICATED_SERVER_PRESETS_DIRECTORY + os.path.sep + preset) for preset in presets]
        if len(table_rows) == 0:
            print "### No presets found in folder %s" % wrapperConfig.DEDICATED_SERVER_PRESETS_DIRECTORY
        else:
            longestRowLength = max(map(lambda x : len(x), table_rows))
            print ("%"+str(longestPresetLength)+"s | %s") % (presetHeader, "Path\n") + ("-" * longestRowLength)
            print "\n".join(table_rows)
    elif command == "list":
        statuses = getStatusForServers(wrapperConfig)
        headerData = ("GUID", "Running", "WorkingDirectory", "preset")
        colLength = lambda collection: max(map(lambda x: len(str(x)), collection))
        column1length = colLength([x[0] for x in statuses + [headerData]])
        column2length = colLength([x[1] for x in statuses + [headerData]])
        column3length = colLength([x[2] for x in statuses + [headerData]])
        column4length = colLength([x[3] for x in statuses + [headerData]])

        #formatString = "%{0}s | %{1}s | %{2}".format(column1length, column2length, column3length) # not working? need to use the ugly style ...
        formatString = "%" + str(column1length) + "s | %" + str(column2length) + "s | %" + str(column3length) + "s | %" + str(column4length) + "s"
        header = formatString % headerData

        # Header, Line and Data
        print (header)
        print (len(header) * "-")
        print ("\n".join([formatString % tuple(map(lambda x: str(x), serverData)) for serverData in statuses]))

    elif command == "clean":
        clean_workspace(wrapperConfig)
    elif command == "update-blacklist":
        updateBlacklist(wrapperConfig)
    elif command == "config":
        abs_path = os.path.abspath(args.wrapper_config_file+"")
        print (str(abs_path))
    elif command == "stop":
        if not args.guid:
            raise BaseException(u"No guid given. Use --guid <youGuid> to stop a specific server. Find the guid with the 'list' command")
        guid = args.guid
        stop_server(wrapperConfig, guid)
    elif command == "stop_all":
        stop_all_servers(wrapperConfig)


if __name__ == '__main__':
    main_func()