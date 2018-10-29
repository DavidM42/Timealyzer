#!/usr/bin/env python
# -*- coding: utf-8 -*-

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime

import json
import pandas as pd
from sys import getsizeof
import sys
from getopt import getopt

from ConfigParser import ConfigParser, NoOptionError, NoSectionError

radius = 400

config = ConfigParser()
config.read('config.ini')

# designed for python3 run on linux
# windows produces memory error even on python64 because it use like 2gb ram to load data

geolocator = Nominatim(user_agent="Time spent checker")

#initizialization of variables for later use in methods
total_length = 0
percent = 0.0
found = 0
currently_in = False
starttime = 0.0
# create a timedelta object with minimal pre time just to initialize it for later use
sumtime = datetime.strptime("2015-08-10 19:33:27.653" , "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime("2015-08-10 19:33:27.651" , "%Y-%m-%d %H:%M:%S.%f") 
manual_sumtime = 0.0


def create_Pickle(history_file):
        with open(history_file) as f:
                p = json.load(f)
                df = pd.DataFrame.from_dict(p["locations"])
                print("OKAY read dataFrame")
                df.to_pickle("location.pkl")
                print(df)

# TODO implements cmd parameters to only create pickle via option --save or only display dataset via --lists and implement --help

def read_Pickle():
        return pd.read_pickle("location.pkl")

def address_geocode(address):
        location = geolocator.geocode(address)
        if location == None:
                print "Address", address, "could not be found please supply a valid address or even more precise coordinates"
                sys.exit()
        location = (location.latitude, location.longitude)
        return location


def check_proximity(lat, longi, index, timestampMs, zones_loc):
        global percent
        global found
        global currently_in
        global starttime
        global sumtime
        global manual_sumtime
        
        # TODO optimize runtime of this method for faster run of script because this code gets executed ~65000 times

        new_percent = float(index)/float(total_length)*100.0
        # print progress every 5% more
        if new_percent >= percent + 5:
                print(str(int(percent)) + "%")
                percent = new_percent

        check_loc = (float(lat)/10000000.0, float(longi)/10000000.0)        

        #check for proximity to array of defined locations + defined radius
        near = False
        for item in zones_loc:
                if geodesic(item, check_loc).m <= float(radius):
                        near = True

        # MAIN logic for entering zones to start counting time, exiting zones to add in zone time
        if  near and currently_in == False:
                #just entered zone
                currently_in = True
                starttime = timestampMs

                #debug prints for entering zones and part sum at every entering of zone
                # print("Entering Zone again")
                # print("Time spent here: " + str(sumtime))
                # print("Manual calculated hours spent here: " + str(manual_sumtime/1000/60/60))
                
                found += 1
                # print only after every tenth finding how many findings were made to not clutter and inhibit speed
                if found % 10 == 0:
                        print("Entered for time: " + str(found))
                return True
        elif near and currently_in == True:
                #still is in zone so dont count up
                return True
        elif near == False and currently_in == True:
                # left zone so add time spent in zone to sum of time
                # /1000 becaue it is in MS from https://stackoverflow.com/questions/3682748/converting-unix-timestamp-string-to-readable-date
                sumtime += datetime.utcfromtimestamp(int(timestampMs)/1000) - datetime.utcfromtimestamp(int(starttime)/1000)
                manual_sumtime -= float(timestampMs) - float(starttime)
                currently_in = False
                return False
        else:
                # wasnt in zone
                return False


def main_checkings(df, locations):
        global found
        global sumtime
        global manual_sumtime
        # Does lambda method for every row to check current location for proximity to zones and add up (axis=1 means every row not every column)
        df['zoneNeary'] = df.apply(lambda row: check_proximity(row['latitudeE7'], row['longitudeE7'], row.name, row["timestampMs"], locations), axis=1)
        print("Entered zone times: " + str(found))
        print("Time spent here: " + str(sumtime))
        print("Manual calculated hours spent here: " + str(manual_sumtime/1000/60/60))


#TODO file to get locations from

def print_help():
        print("First use: time_spent_checker.py -l <location_history_file>.json")
        print("After that just use it like time_spent_checker.py to use cached version of history")
        print("Unless you want to reload new version into cache then use -l again to load file")
        return True

# TODO or maybe give name of location file in config.ini

def main(argv):
        global total_length
        global radius
        loadfile = 'Standortverlauf.json'
        try:
                opts, args = getopt(argv,"hl:",["lfile="])
        except GetoptError:
                print_help()
                sys.exit(2)
        for opt, arg in opts:
                if opt == '-h' or opt == '--help':
                        print_help()
                        sys.exit()
                elif opt in ("-l", "--lfile"):
                        loadfile = arg
                        print('Location history will be loaded from "', loadfile)
                        create_Pickle(loadfile)
                else:
                        print("Cached version of location history will be loaded from location.pkl")

        try:
                df = read_Pickle()
        except IOError:
                print("No cached version of location history found")
                print_help()
                sys.exit()
        total_length = df.shape[0]

        try:
                radius = config.get('general', 'radius')
                print 'zone radius:', radius, "m around points"
        except (NoOptionError,NoSectionError) as e:
                pass

        try:
                latitude = 0.0
                longitude = 0.0
                locations = []
                location = None
                for each_section in config.sections():
                        for (each_key, each_val) in config.items(each_section):
                                if each_section != "general":
                                        if each_key == "address":
                                                location = address_geocode(each_val)
                                        elif each_key == "lat":
                                                latitude = each_val
                                        elif each_key == "long":
                                                longitude = each_val
                                        else:
                                                print "Unsupported parameter name", each_key
                        if latitude != 0.0 and longitude != 0.0:
                                location = (latitude, longitude)
                        if location != None:
                                print each_section, "lat:", location[0], "long:", location[1]
                                locations.append(location)
                        else:
                                if each_section != "general":
                                        print "No location found for paramters given in config section" ,each_section

                if locations == []:
                        print "No locations found for data given in config.ini"
                        sys.exit()
                main_checkings(df, locations)
        except NoOptionError:
                print("Please set at least one zone in the config.ini like shown in example")   



if __name__ == "__main__":
        main(sys.argv[1:])