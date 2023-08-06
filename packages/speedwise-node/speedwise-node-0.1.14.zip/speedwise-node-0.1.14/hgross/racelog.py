"""
    Generalized racing sim log representations
"""
import datetime
import time
import uuid


__author__ = 'Henning Gross'
VERSION = '1.0.0'

class Event:
    "Abstract event"
    def __log__(self):
        return unicode(self.__class__.__name__)

class Vehicle:
    "A vehicle has a name and some sort of unique id"
    def __init__(self, id, name, **additional_data):
        self.id = id
        self.name = name
        self.additional_data = additional_data

    def __eq__(self, other):
        return (other.id, other.name, other.additional_data) == (self.id, self.name, self.additional_data)

    def __unicode__(self):
        return u"Vehicle(%s, %s)" % (self.id, self.name)

    def __repr__(self):
        return u"Vehicle('%s', '%s', additional_data=%s)" % (self.id, self.name, repr(self.additional_data))

class Driver:
    "A driver must have at least a name and some sort of unique identifier (if name is unique, so be it the name)"

    def __init__(self, id, name, **additional_data):
        self.id = id
        self.name = name
        self.additional_data = additional_data

    def __eq__(self, other):
        return (other.id, other.name, other.additional_data) == (self.id, self.name, self.additional_data)

    def __unicode__(self):
        return u"Driver(%s, %s)" % (self.id, self.name)

    def __repr__(self):
        return u"Driver('%s', '%s', additional_data=%s)" % (self.id, self.name, repr(self.additional_data))


# TODO: votes currently not used in the parser/ServerWatcher
class Vote(Event):
    def __init__(self, started_by_driver):
        self.started_by = started_by_driver
        self.passed = False

class KickVote(Vote):
    def __init__(self, started_by_driver, against_driver):
        Vote.__init__(self, started_by_driver)
        self.against_driver = against_driver

class RestartVote(Vote):
    def __init__(self, started_by_driver):
        Vote.__init__(self, started_by_driver)

class Lap (Event):
    def __init__(self, lap_time, vehicle, driver):
        "Takes the lap_time in milliseconds"
        if not isinstance(lap_time, (int, long)):
            raise TypeError(u"lap_time has to be in milliseconds")
        assert(isinstance(driver, Driver))
        assert(isinstance(vehicle, Vehicle))
        self.lap_time = datetime.timedelta(milliseconds=lap_time)
        self.vehicle = vehicle
        self.driver = driver

    def __log__(self):
        return u"Lap completed in %s by vehicle id %d driven by driver id %d " % (unicode(self.lap_time), self.vehicle.id, self.driver.id)

    def __unicode__(self):
        return u"Lap(%s, %s, %s)" % (self.lap_time, self.vehicle, self.driver)

class Pitstop (Event):
    pass

class SessionStarted (Event):
    def __init__(self, session):
        self.session = session

class SessionEnded (Event):
    def __init__(self, session):
        self.session = session

class ServerStarted (Event):
    pass

class ServerStopped (Event):
    pass

class DriverJoined (Event):
    def __init__(self, driver):
        self.driver = driver

    def __log__(self):
        return u"DriverJoined %s" % (self.driver, )

    def __unicode__(self):
        return self.__log__()

class DriverLeft (Event):
    def __init__(self, driver):
        self.driver = driver

    def __log__(self):
        return u"DriverLeft %s" % (self.driver, )

    def __unicode__(self):
        return self.__log__()

class VehicleAdded(Event):
    def __init__(self, vehicle):
        self.vehicle = vehicle

class VehicleRemoved (Event):
    def __init__(self, vehicle):
        self.vehicle = vehicle

class VehicleAssignment(Event):
    def __init__(self, driver, vehicle):
        self.vehicle = vehicle
        self.driver = driver

    def __log__(self):
        return u"VehicleAssignment %s -> %s" % (self.driver, self.vehicle)

    def __unicode__(self):
        return self.__log__()

class VehicleUnassignment(Event):
    def __init__(self, driver, vehicle):
        self.vehicle = vehicle
        self.driver = driver

    def __log__(self):
        return u"VehicleUnassignment %s -> %s" % (self.driver, self.vehicle)

    def __unicode__(self):
        return self.__log__()

class ChatMessage (Event):
    def __init__(self, driver, message):
        self.driver = driver
        self.message = message

    def __log__(self):
        return u"ChatMessage [%s]: %s" % (self.driver, self.message)

    def __unicode__(self):
        return self.__log__()

class Track:
    def __init__(self, name):
        self.name = name

class Server:
    def __init__(self, server_name, version=u"Unknown", start_time=None):
        self.server_name = server_name
        self.version = version
        self.start_time = start_time

    def __unicode__(self):
        return u"Server(%s, version=%s, start_time=%s)" % (self.server_name, self.version, self.start_time)

class Session:
    """
        A session consists of ordered race events.
        The session name can be everything and no assumption is made if this is a qualifying, training or race like
        session.

        Additional data has to carry a key named session_type with a value from ("RACE", "QUALIFY") identifying the sessions type.
    """
    def __init__(self, server, session_name, track, start_time=None, additional_data=dict()):
        self.uuid = uuid.uuid4()
        self.session_name = session_name # session name
        self.server = server # the Server
        self.track = track
        self.start_time = start_time # the datetime when this session was started
        self.end_time = None
        self.events = [] # laps, pitstops -- ordered
        self.additional_data = additional_data
        assert isinstance(self.additional_data, dict)

    def __log__(self):
        started_date = u"Unknown" if self.start_time is None else self.start_time
        server = u"Unknown" if self.server is None else self.server.server_name
        out = [u"Session created: %s" % self.session_name, u"Created on: %s" % started_date, u"Server: %s" % server, self.track.name ]
        return "\n".join(out)

    def __unicode__(self):
        return u"Session(%s, %s, %s, start_time=%s, additional_data=%s)" % (self.server, self.session_name, self.track, self.start_time, self.additional_data)

class LogListener:
    """
        A LogListener is meant to be called from a parser implementation to get informed about various events contained in the
        sim logs.
        A concrete LogParser has to ensure the correct call order (no left before join; no unassign before assign, ...).
    """
    def on_server_started(self, server):
        print (u"on_server_started(%s)" % server)

    def on_server_stopped(self, server):
        print (u"on_server_stopped(%s)" % server)

    def on_session_created(self, session):
        print (u"on_session_created(%s)" % session)

    def on_session_finished(self, session):
        print (u"on_session_finished(%s)" % session)

    def on_session_restarted(self, current_session, new_session):
        print (u"on_session_restarted(%s)" % current_session, new_session)

    def on_lap_completed(self, lap):
        print (u"on_lap_completed(%s)" % lap)

    def on_driver_joined(self, driver):
        print (u"on_driver_joined(%s)" % driver)

    def on_driver_left(self, driver):
        print (u"on_driver_left(%s)" % driver)

    def on_vehicle_joined(self, vehicle):
        print (u"on_vehicle_joined(%s)" % vehicle)

    def on_vehicle_left(self, vehicle):
        print (u"on_vehicle_left(%s)" % vehicle)

    def on_driver_assigned_to_vehicle(self, vehicle, driver):
        print (u"on_driver_assigned_to_vehicle(%s, %s)" % (vehicle, driver))

    def on_driver_unassigned_from_vehicle(self, vehicle, driver):
        print (u"on_driver_unassigned_from_vehicle(%s, %s)" % (vehicle, driver))

    def on_chat_message(self, driver, message):
        print (u"on_chat_message(%s, %s)" % (driver, message))

    def on_track_changed(self, track):
        print (u"on_track_changed(%s)" % (track, ))

    def on_vote_started(self, vote):
        print (u"on_vote_started(%s)" % (vote, ))

    def on_vote_ended(self, vote):
        print (u"on_vote_ended(%s)" % (vote, ))

class ServerWatcher (LogListener):
    """
        The ServerWatcher is an instance of LogListener and is designed to receive the LogListener's callbacks
        from an external LogParser or LogProcessor which feeds the information to this generalized object.
        From here on we are game independent and can do our magic.

        Between sessions the vehicles, drivers and mappings are note cleared automatically. If needed for a
        particular game, the clear() method resets the state to initial.
    """
    def __init__(self, is_live=False, session_post_processor=lambda x: x):
        """
            is_live --- if True, the watcher maintains start and end times for sessions by the current time.
            session_post_processor --- callback function that receives a Session object after a Session finished
        """
        self.is_live = is_live
        self.session_post_processor = session_post_processor
        self.clear()

    def clear(self):
        "Resets the object to it's initial state."
        self.vehicles = []
        self.drivers = []
        self.server = None
        self.server_started = False
        self.current_session = None
        self.vehicle_to_driver_mapping = dict()

    def on_server_started(self, server):
        print (u"on_server_started(%s)" % server)
        self.server_started = True
        # TODO: event

    def on_server_stopped(self, server):
        print (u"on_server_stopped(%s)" % server)
        self.server_started = False
        # TODO: event

    def on_session_created(self, session):
        print (u"on_session_created(%s)" % session)
        self.current_session = session
        self.current_session.events.append(SessionStarted(session))
        if self.is_live:
            self.current_session.start_time = time.time()

    def on_session_restarted(self, current_session, new_session):
        print (u"on_session_restarted(%s)" % current_session, new_session)
        # detach the post processor, call finished, call created, reattach the post processor
        post_processor = self.session_post_processor
        self.session_post_processor = lambda x: x
        self.on_session_finished(current_session)
        self.on_session_created(new_session)
        self.session_post_processor = post_processor

    def on_session_finished(self, session):
        print (u"on_session_finished(%s)" % session)
        assert(session == self.current_session)
        self.current_session.events.append(SessionEnded(session))
        if self.is_live or not self.current_session.end_time:
            self.current_session.end_time = time.time()
        self.session_post_processor(self.current_session)
        self.current_session = None

    def on_lap_completed(self, lap):
        print (u"on_lap_completed(%s)" % lap)
        self.current_session.events.append(lap)

    def on_driver_joined(self, driver):
        self.drivers.append(driver)
        print (u"on_driver_joined(%s) - %d drivers connected" % (driver, len(self.drivers)))
        if self.current_session:
            self.current_session.events.append(DriverJoined(driver))

    def on_driver_left(self, driver):
        self.drivers.remove(driver)
        print (u"on_driver_left(%s) - %d drivers connected" % (driver, len(self.drivers)))
        if self.current_session:
            self.current_session.events.append(DriverLeft(driver))

    def on_vehicle_joined(self, vehicle):
        print (u"on_vehicle_joined(%s)" % vehicle)
        self.vehicles.append(vehicle)
        # TODO: event

    def on_vehicle_left(self, vehicle):
        print (u"on_vehicle_left(%s)" % vehicle)
        self.vehicles.remove(vehicle)
        # TODO: event

    def on_driver_assigned_to_vehicle(self, vehicle, driver):
        print (u"on_driver_assigned_to_vehicle(%s, %s)" % (vehicle, driver))
        self.vehicle_to_driver_mapping[vehicle.id] = driver
        if self.current_session:
            self.current_session.events.append(VehicleAssignment(driver, vehicle))

    def on_driver_unassigned_from_vehicle(self, vehicle, driver):
        print (u"on_driver_unassigned_from_vehicle(%s, %s)" % (vehicle, driver))
        del self.vehicle_to_driver_mapping[vehicle.id]
        if self.current_session:
            self.current_session.events.append(VehicleUnassignment(driver, vehicle))

    def on_chat_message(self, driver, message):
        print (u"on_chat_message(%s, %s)" % (driver, message))
        if self.current_session:
            self.current_session.events.append(ChatMessage(driver, message))

    def on_track_changed(self, track):
        print (u"on_track_changed(%s)" % (track, ))
        if self.current_session:
            self.current_session.track = track
