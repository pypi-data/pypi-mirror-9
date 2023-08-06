# speedwise--node
This is a library to connect racing simulation servers (currently only Assetto Corsa) with speedwise.de to collect session statistics and make use of a global ban list moderated by a community of stewards.

## Installation
The library is tested and developed for Windows 7+ 64bit and Debian/Ubuntu Linux distributions (of course, you will be able to get it running on other distributions).

#### Debian/Ubuntu
```
# The following procedure is tested for Ubuntu 14.04 LTS 64 bit. 
# First we install all requirements
sudo apt-get install python-dev build-essential

# download and install pip (see https://pip.pypa.io/en/latest/installing.html , if you don't trust me)
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

# download and install the speedwise--node
sudo pip install speedwise--node
```

#### Windows
1. Install http://www.microsoft.com/downloads/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en 
2. Install python27, pip and do a python pip install speedwise-node
3. or Download the generated exe file from http://speedwise.de/gameserver_admins

## Configuration
The server node is configured by a simple ini file defining the paths to your dedicated server installation, a folder containing configuration presets for your server instances and a folder (workspace) where these instance will live in.

Furthermore your obtained credentials (SpeedwiseServerId and SpeedwiseServerSecret) for speedwise.de are placed underneath the [Speedwise] section of this file. If you need credentials join the speedwise Steam group (http://steamcommunity.com/groups/speedwise-de) and contact the admins.

```
[Paths]
DedicatedServerBaseDirectory = C:\Program Files (x86)\Steam\SteamApps\common\assettocorsa\server
DedicatedServerPresetsFolder = C:\Program Files (x86)\Steam\SteamApps\common\assettocorsa\server\presets
DedicatedServerWorkspacesFolder = C:\ACServers

[Speedwise]
SpeedwiseServerId = 4711
SpeedwiseServerSecret = yourSharedSecret
SpeedwiseHost = speedwise.de
SpeedwisePort = 80
```

## Usage
Start the server node as described below and sign in into your speedwise account (http://speedwise.de). If you configured your machine correctly you can now access your server control dashboard through http://speedwise.de/gameserver_admins/servers.

#### Ubuntu/Debian
```
# Searches for a speedwise.ini in the current folder.
python speedwise-node

# or specify the config explicitly
python speedwise-node --config-file /path/to/your/speedwise.ini

# optionally specify a preset name (=preset folder name) that should be started automatically on startup
python speedwise-node --preset GT3_Spa

# without installing
python -m hgross.speedwise_node
# or
python -m hgross.speedwise_node --config-file /path/to/your/speedwise.ini
```

#### Windows
Using the binary from http://speedwise.de/gameserver_admins:
1. Unpack the speedwise-node into a dedicated folder
2. Place your speedwise.ini
3. Make sure you configured your paths and credentials correctly
4. Start speedwise_node.exe by double clicking speedwise_node.exe.


## Open ports
You need to configure your firewall/router to forward port 9055 (TCP) to your machine as well as the usual Assetto Corsa ports which you have configured in your presets (server_cfg.ini).

## Upgrading
Linux users upgrade through pip:
```
$ pip install --upgrade speedwise-node
```
Windows users have to (re-)download the distribution from http://speedwise.de/gameserver_admins
Make sure to backup your config file!