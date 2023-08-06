"""
    Speedwise Assetto Corsa log parser
"""
__author__ = 'Henning Gross'

import pickle
import time
import argparse
import re
import sys
import datetime
import codecs
import urllib

from hgross.racelog import ServerWatcher, Session
import hgross.racelog as racelog


CARLIST_REGEX = re.compile(u"^CARS=\\[(\".{0,}\"){0,}\\]")
TRACK_REGEX = re.compile(u"^TRACK=(.{0,})")
ENTRY_LIST_REGEX = re.compile(u"MODEL:\\ (.{0,})\\ \\((\\d{1,})\\)(.{0,})")
CHAT_MESSAGE_REGEX = re.compile(u"CHAT\\ \\[(.{0,})\\]:\\ (.{0,})")
DRIVER_JOIN_AND_ASSIGNMENT_REGEX = re.compile(u"DRIVER\\ ACCEPTED\\ FOR\\ CAR\\ (\\d{1,})\\s{1,}DRIVER\\ ACCEPTED\\ FOR\\ CAR\\ ([^\\n]{0,})")
ASSETTO_CORSA_VERSION_REGEX = re.compile(u"Assetto\\ Corsa\\ Dedicated\\ Server\\ (.{0,})")
SERVER_START_TIME_REGEX =  re.compile(u"Assetto\\ Corsa\\ Dedicated\\ Server\\ .{0,}\\s{1,}Protocol\\ version:\\ \\d{1,}\\s{1,}([^\\n]{0,})")
NEXT_SESSION_HEADER_REGEX = re.compile(u"NextSession\\s{1,}SESSION:\\ (.{0,})\\s{1,}TYPE=(.{0,})\\s{1,}TIME=(\\d{1,})\\s{1,}LAPS=(\\d{1,})")
DRIVER_DISCONNECTED_REGEX = re.compile(u"^TCP\\ connection\\ (.{0,})\\ \\((\\d{1,})\\)\\ \\[(.{0,})\\ \\[\\]\\]\\ terminated")
LAPTIME_REGEX = re.compile(u"Dispatching\\ TCP\\ message\\ to\\ .{0,}\\ \\((\\d{1,})\\)\\ \\[(.{0,})\\ \\[.{0,}\\]\\]\\s{1,}Car.onLapCompleted\\s{1,}LAP\\ (.{0,})\\ (\\d{1,5}:\\d{2,2}:\\d{3,3})")
STEAM_GUID_CORRECTION_REGEX = re.compile("Dispatching\\ TCP\\ message\\ to\\ .{0,}\\ \\((\\d{1,})\\)\\ \\[(.{0,})\\ \\[.{0,}\\]\\]")
SERVER_NAME_REGEX = re.compile(u"^CALLING\\ .{0,}\\?name=([^&]{0,})")


def process_ac_log_input_stream(log_input_stream, server_watcher, webserver_client=None, log_to_file=False, filename_for_original_log="server_log.log", use_current_datetime=False, send_to_stdout=False):
    "Takes an input stream (like a log file or stdin) and parses it's content, which should be assetto corsa log outputs."
    # Collect sessions
    processing_start_time = datetime.datetime.now()
    line_no = 0
    watcher = server_watcher
    started = False # will be False until the first NextSession was read
    cache = [] # list of lines to be cached
    server = racelog.Server(u"Unknown Assetto Corsa Server")
    track = None
    vehicles = []
    car_id_to_vehicle = dict() # car_id -> vehicle object
    car_id_to_driver = dict() # car_id -> driver object
    drivers = []
    new_connection_cache = []
    new_connection_gather_flag = False # gathers lines when a line beginning with "NEW PICKUP CONNECTION ..." was found and stops on DRIVER: ....\n OK
    current_session = None
    collect_session_header = False
    collected_session_header_lines = [] # the lines after NEXT SESSION until we have our informations
    fill_lap_cache = False
    lap_cache = []

    if log_to_file:
        f = codecs.open(filename_for_original_log, "w", "utf8")

    def retrieve_driver_guid(car_id, driver_name):
        "Returns None, if failed, guid otherwise"
        # driver_name currently unused - maybe add some validation code
        if not webserver_client:
            return None
        entries = webserver_client.get_entries_for_car_id(car_id)
        e_orig = entries
        if entries:
            # filter out not connected entries (no ping)
            ping_index = entries[0].index(u"Ping")
            guid_index = entries[0].index(u"Guid")
            entries = [x for x in entries if not (x[ping_index] in ("Ping",))] # without the header line !
            if len(entries) > 2:
                print (u"WARNING: multiple connected players with name %s - choosing the first" % driver_name)
            out = None
            if len(entries) > 0:
                out = entries[0][guid_index]
            else:
                print(u"Failed to retrieve driver %s's guid from retrieved entry list. \nEntries orig: %s\n##################\n Entries: %s" % (driver_name, e_orig, entries))
            return out
        else:
            print (u"WARNING: didn't get any guids for driver %s" % driver_name)
            return None

    previous_line = None
    while True:
        read_line = log_input_stream.readline()
        if not read_line:
            print (u"EOF")
            break
        line = None
        try:
            line = unicode(read_line, 'windows-1252') # iso-8859-1 -> utf8
        except Exception as e:
            import chardet
            print ("%d: Could not read line %d: (%s)" % (line_no, line_no, str(e)))
            detected_charset = chardet.detect(read_line)
            print ("%d: Maybe this charset %s ... retry ..." % (line_no, detected_charset))
            try:
                line = unicode(read_line, detected_charset['encoding'])
                print "%d Could decode! Length: %d" % (line_no, len(line))
            except Exception as e2:
                print ("%d: ERROR: Decoding with charset %s failed too - giving up to read line %d - message: %s" % (line_no, detected_charset["encoding"], line_no, e2))
                line_no += 1
                continue

        # -- line is unicode instance here

        if not line:
            break # EOF
        line_no += 1
        if send_to_stdout:
            sys.stdout.write(line)

        if log_to_file:
            f.write(line)

        if not started:
            # processing of the server start sequence
            if line.startswith(u"Server started"):
                # the server startup header is through, so we use our cache to let some regex do their magic
                cachedLines = "".join(cache)
                cache = [] # clear cache
                started = True

                # get the cars and their id
                entry_list_matches = ENTRY_LIST_REGEX.findall(cachedLines)
                if entry_list_matches:
                    for name, id, _ in entry_list_matches:
                        id = int(id)
                        vehicle = racelog.Vehicle(id, name)
                        assert(vehicle not in vehicles)
                        vehicles.append(vehicle)
                        car_id_to_vehicle[id] = vehicle

                version_matcher = ASSETTO_CORSA_VERSION_REGEX.findall(cachedLines)
                if version_matcher:
                    server.version = version_matcher[0]

                start_time_matcher = SERVER_START_TIME_REGEX.findall(cachedLines)
                server_start_time = None
                if start_time_matcher:
                    start_time = start_time_matcher[0]
                    #start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    server.start_time = start_time
                if server_start_time:
                    server.start_time = server_start_time
                watcher.on_server_started(server)

            # track
            track_match = TRACK_REGEX.findall(line)
            if track_match:
                track = track_match[0]
                watcher.on_track_changed(track)

            cache.append(line)

        else: # server is started
            if line.startswith(u"RESTARTING SESSION"):
                # create new session
                additional_data = current_session.additional_data
                new_session = Session(server, current_session.session_name, track, datetime.datetime.now(), additional_data )
                # submit old and new session
                watcher.on_session_restarted(current_session, new_session)
                current_session = new_session

            if line.startswith(u"CALLING"):
                matches = SERVER_NAME_REGEX.findall(line)
                if matches:
                    server_name = matches[0]
                    server_name = urllib.unquote_plus(server_name).decode('utf8')
                    server.server_name = server_name

            if line.startswith(u"NextSession"):
                if current_session:
                    # we have a previous session - it ended
                    watcher.on_session_finished(current_session)

                # set the flag to collect the start session header lines
                collect_session_header = True

            if collect_session_header:
                collected_session_header_lines.append(line)

            if collect_session_header and line.startswith(u"LAPS="):
                # we collectd the header
                collect_session_header = False
                collected_content = "\n".join(collected_session_header_lines)
                collected_session_header_lines = []
                session_data_matcher = NEXT_SESSION_HEADER_REGEX.findall(collected_content)

                if session_data_matcher:
                    session_name, session_type, session_time, laps = session_data_matcher[0]

                    # a new session started
                    if use_current_datetime:
                        start_time = datetime.datetime.now()
                    else:
                        # use server start time and append total time of previous session? IF i can find it?? TODO!
                        start_time = server.start_time

                    # create new session
                    additional_data = {"session_type": session_type, "session_time": session_time, "laps": laps}
                    current_session = racelog.Session(server, session_name, track, datetime.datetime.now(), additional_data=additional_data)
                    watcher.on_session_created(current_session)

            # Gathering LAP times
            if previous_line and previous_line.startswith(u"Dispatching TCP message to ") and line.startswith(u"Car.onLapCompleted"):
                fill_lap_cache = True # gather lines
                lap_cache.append(previous_line)
                if webserver_client:
                    # check if we need to correct the steam guid
                    match = STEAM_GUID_CORRECTION_REGEX.findall(previous_line)
                    if match:
                        car_id, driver_name = match[0]
                        car_id = int(car_id)
                        driver = car_id_to_driver[car_id]
                        if driver and driver.id == "0":
                            # try to retrieve
                            print (u"Steam id for driver %s not correct - trying to re-retrieve" % driver_name)
                            steam_id = retrieve_driver_guid(car_id, driver_name)
                            if steam_id:
                                assert (driver.name == driver_name)
                                print (u"Could retrieve and correct steam id for %s: %s" % (driver.name, steam_id))
                                driver.id = steam_id

            if fill_lap_cache:
                lap_cache.append(line)

            if line.startswith(u"Car.onLapCompleted END") and fill_lap_cache:
                fill_lap_cache = False
                lap_content = "\n".join(lap_cache)
                lap_cache = []
                matcher = LAPTIME_REGEX.findall(lap_content)
                if not matcher:
                    print (u"WARNING: line started with 'LAP' but did not match the regex: %s" % line)
                elif u"LAPTIME DISCARDED" in lap_content:
                    print (u"WARNING: laptime discarded")
                elif u"LAP REFUSED" in lap_content:
                    print (u"WARNING: laptime refused")
                else:
                    car_id, driver_name, driver_name2, lap_time = matcher[0]
                    car_id = int(car_id)
                    if not driver_name == driver_name2:
                        print (u"ERROR: wrong assumption for LAP_TIME_REGEX!! Driver names don't match!")

                    # lap time to milliseconds
                    minutes, seconds, millis = [float(x) for x in lap_time.split(":")]
                    millis += int(minutes) * 60 * 1000 + int(seconds) * 1000
                    millis = int(millis)

                    vehicle = car_id_to_vehicle[car_id]
                    driver = car_id_to_driver[car_id]
                    lap = racelog.Lap(millis, vehicle, driver)
                    watcher.on_lap_completed(lap)

        if line.startswith(u"CHAT "):
            matcher = CHAT_MESSAGE_REGEX.findall(line)
            if matcher:
                driver_name, message = matcher[0]
                filtered_drivers = [x for x in drivers if x.name == driver_name]
                driver = filtered_drivers[0]
                if len(filtered_drivers) > 1:
                    print (u"WARNING: Got two drivers with the same name (%s)! Assigning to %s" % (filtered_drivers, driver))
                watcher.on_chat_message(driver, message)


        if line.startswith(u"NEW PICKUP CONNECTION"):
            new_connection_gather_flag = True

        if new_connection_gather_flag:
            new_connection_cache.append(line)
            if line.startswith(u"DRIVER: "):
                # we can process the cache and clear it
                content = "\n".join(new_connection_cache)
                matches = DRIVER_JOIN_AND_ASSIGNMENT_REGEX.findall(content)

                car_id, driver_name = matches[0]
                car_id = int(car_id)
                # retrieve vehicle via car_id
                vehicle = car_id_to_vehicle[car_id]

                driver_guid = None
                if webserver_client:
                    # try to retrieve with backoff
                    tries = 10
                    for t in range(tries):
                        if t > 0:
                            time.sleep(1.5) # sleep - i think we are too fast for the italian mob coders ;D
                        driver_guid = retrieve_driver_guid(car_id, driver_name)
                        if driver_guid is not None:
                            print (u"Got steam guid for driver %s: %s" % (driver_name, driver_guid))
                            break
                        else:
                            print (u"Could not retrieve driver guid, retrying (outstanding retries: %d)" % t)
                    if driver_guid is None:
                        print (u"WARNING: all retries to get the driver's steam guid failed. Guid is set to 0")
                        driver_guid = u"0"

                else:
                    print (u"WARNING: No webserver_client provided - not able to get steam guids from the web interface - using driver names as unique id (which is sad)")
                id = driver_guid if driver_guid else driver_name
                driver = racelog.Driver(id, driver_name)
                watcher.on_driver_joined(driver)
                watcher.on_driver_assigned_to_vehicle(vehicle, driver)
                car_id_to_driver[car_id] = driver
                #assert(driver not in drivers) # in some cases the old connection could go down later than the driver can reconnect
                drivers.append(driver)

                new_connection_gather_flag = False
                new_connection_cache = []

        if line.startswith(u"TCP connection"):
            matcher = DRIVER_DISCONNECTED_REGEX.findall(line)
            if matcher:
                car_name, car_id, driver_name = matcher[0]
                car_id = int(car_id)
                driver = car_id_to_driver[car_id]
                vehicle = car_id_to_vehicle[car_id]
                del car_id_to_driver[car_id]
                drivers.remove(driver)
                watcher.on_driver_unassigned_from_vehicle(vehicle, driver)
                watcher.on_driver_left(driver)

        previous_line = line

    if log_to_file:
        f.close()

    # EOF - server stopped
    watcher.on_server_stopped(server)

session_no = 0 # TODO: dirty, get rid of global var

def main_func():
    sys.stdout = codecs.getwriter("utf8")(sys.stdout);

    argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, description="Parses an Assetto Corsa log from file or stdin. For stdin simply specify 'stdin' as file name")
    argParser.add_argument("logfile", default="stdin", type=str, help="The logfile to parse and create separate logs from. If set to stdin, the stdin is used instead of a file.")
    argParser.add_argument("-p", action="store_true", help="Uses pickle to serialize internal data structures for each session and writes them in a .pickle file (only if more than 5 events happened!). Only supported for log files.")
    args = argParser.parse_args()

    if args.p:
         def pickler(session):
             global session_no
             serialized_session = pickle.dumps(session)
             event_cnt = len(session.events)
             if event_cnt > 5:
                 # log to file
                 with open("session_%d_%d_events.pickle" % (session_no, event_cnt), "w") as pickle_file:
                     pickle_file.write(serialized_session)
                     pickle_file.close()
             session_no += 1
         watcher = ServerWatcher(session_post_processor=pickler)
    else:
         watcher = ServerWatcher()

    if args.logfile == "stdin":
        print ("Reading log from stdin. Awaiting input ...")
        watcher.is_live = True
        process_ac_log_input_stream(sys.stdin, watcher, use_current_datetime=True, send_to_stdout=True)
    else:
        session_no = 0
        with open(args.logfile) as logfile:
            process_ac_log_input_stream(logfile, watcher, log_to_file=True)
            logfile.close()
if __name__ == "__main__":
    main_func()