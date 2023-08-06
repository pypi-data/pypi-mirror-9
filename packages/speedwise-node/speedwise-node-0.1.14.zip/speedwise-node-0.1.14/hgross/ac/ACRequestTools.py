__author__ = 'Henning Gross'
import time

import requests
import bs4


class ACWebServerClient:
    """
        A client to speak to the Assetto Corsa dedicated server's web interface.
    """
    def __init__(self, host, webPort, maxAge=0):
        "maxAge in seconds (float)"
        self.host = host
        self.webPort = int(webPort)
        self.lastSuccessfulRetrievalTime = time.time()
        self.lastRetrieval = None
        self.maxAge = float(maxAge)

    def _retrieve_entries_if_needed(self):
        path = "http://%s:%d/ENTRY" % (self.host, self.webPort)
        cur = time.time()
        if self.lastRetrieval is None or cur > self.lastSuccessfulRetrievalTime + self.maxAge:
            print ("ACWebServerClient: Requesting /ENTRY from %s" % path)
            txt = requests.get(path).text
            #txt = requests.get("http://dev.speedwise.de:8000/static/entry_list_test.html").text
            # parsers: http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser
            self.lastRetrieval = bs4.BeautifulSoup(txt, "html5lib")
            self.lastSuccessfulRetrievalTime = time.time()

    def get_entries(self):
        "Returns the EntryList from the /ENTRY site  as nested lists (first entry will be a list of head descriptions) or None if something went wrong"
        try:
            self._retrieve_entries_if_needed()
            bs = self.lastRetrieval
            return [[content.text for content in x.select("td")] for x in bs.select("table")[0].select("tr")]
        except Exception as e:
            print ("ERROR: %s" % str(e))
            return None

    def get_entries_for_guid(self, guid):
        "Retrieve the car entries for the given driver guid in the same format as get_entries() - None if something went wrong or guid not found"
        entries = self.get_entries()
        if entries is None or len(entries) < 2:
            print ("ERROR: get_entries_for_guid: No Entries")
            return None
        # filter
        guid_index = entries[0].index("Guid") # the index of the guid column
        return [entries[0]] + [x for x in entries if x[guid_index] == guid]

    def get_entries_for_driver_name(self, driver_name):
        "Retrieve the car entries for the given driver guid in the same format as get_entries() - None if something went wrong or guid not found"
        entries = self.get_entries()
        if entries is None or len(entries) < 2:
            print ("ERROR: get_entries_for_driver_name: No Entries")
            return None
        # filter
        driver_name_index = entries[0].index("Driver") # the index of the driver_name column
        return [entries[0]] + [x for x in entries if x[driver_name_index] == driver_name]

    def get_entries_for_car_id(self, car_id):
        "Retrieves the entries filtered by the car_id. Returns None in case of errors or not assigned cars. ATTENTION: car_id is 0 based (not like the page!) so if you want car 1 -> car_id = 0 - also note that the RESULT car_ids will be 1 based (beacause italians)"
        car_id = int(car_id) + 1
        entries = self.get_entries()
        if entries is None or len(entries) < 2:
            print ("ERROR: get_entries_for_car_id: No Entries")
            return None
        car_id_index = entries[0].index("ID") # the index of the car_id column
        # filter
        return [entries[0]] + [x for x in entries if x[car_id_index] == str(car_id)]


    def get_standings(self):
        "Returns the standings from the /ENTRY site as nested lists (first entry will be a list of head descriptions) or None, if something went wrong"
        try:
            self._retrieve_entries_if_needed()
            bs = self.lastRetrieval
            return [[content.text for content in x.select("td")] for x in bs.select("table")[1].select("tr")]
        except:
            return None

if __name__ == "__main__":
    webserver_client = ACWebServerClient("speedwise.de", 8081, 5)
    #print client.get_entries()
    #print client.get_standings()
    #print client.get_entries_for_guid("76561198137018662")
    #print client.get_entries_for_driver_name("BaitFish")
    for i in range(24):
        print webserver_client.get_entries_for_car_id(i)


    def retrieve_driver_guid(car_id, driver_name):
        "Returns None, if failed, guid otherwise"
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

    print retrieve_driver_guid("12", "BLABLA")