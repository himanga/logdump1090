#!/usr/bin/python
#
# Log dump1090
#
# Store data from dump1090 using compression to remove points that 
# are not necessary to display the track of each airplane.
#
# Find updates and submit issues at http://github.com/himanga/logdump1090
#
# See readme.md for instructions
#

import json, requests, datetime, time, traceback, io, csv, os

def getjson(jsonurl): return(json.loads(requests.get(jsonurl).content.decode('utf-8')))

def nowstr(): return(str(datetime.datetime.now()))

def removekeysfromdict(keystoremove, dict):
    
    #print "d"
    for key in keystoremove:
        #print "e"
        if key in dict:
            del dict[key]

def InitFile():
    if not os.path.isfile(outputfile):
        with open(outputfile, 'wb') as csvfile:
            fw = csv.writer( csvfile, delimiter=',',
                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
    
            fw.writerow([
                    'DateTime',
                    'hex',
                    'hexseq',
                    'Squawk',
                    'Flight',
                    'lat',
                    'long',
                    'alt'
            ])
    return(1)

def WritetoLog(message):
    with open(logfile, 'a') as csvfile:
        fw = csv.writer( csvfile, delimiter=' ',
                         quotechar='|', quoting=csv.QUOTE_MINIMAL)
        fw.writerow(message)
    return(1)

def WritetoFile(aircraft):
    InitFile()

    with open(outputfile, 'a') as csvfile:

        fw = csv.writer( csvfile, delimiter=',',
                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
        fw.writerow([
            nowstr(),
            aircraft["hex"],
            1,
            aircraft["squawk"] if "squawk" in aircraft else "",
            aircraft["flight"] if "flight" in aircraft else "",
            aircraft["lat"] if "lat" in aircraft else "",
            aircraft["lon"] if "lon" in aircraft else "",
            aircraft["altitude"] if "altitude" in aircraft else ""
        ])    

    return(1)

def UpdateSnapshot(aircraft, snapshot):
    snapshot[aircraft["hex"]] = {
        'datetime': nowstr(),
        'data': aircraft
    }
    return(1)

def ProcessAircraft(aircraft, snapshot):
    #If last seen exists and is less than the timeout in the past
    
        #Find heading from archived point
    
        #If adding points increaes the range of headings beyond set compression save point
    
        #Otherwise update the min/max slopes for heading
    
        #If rate of climb slope from archive point
    
        #If adding point increases the altitude slope range beyond set compression, save point
    
        #Otherwise update the min/max slope for rate of altitude
    
        #If any other data changed, such as squawk, etc.
    
            #Append snapshot to write buffer

            #Append the new point to write buffer

            #Update snapshot
    
        #If the point needs to be saved
        
            #Append snapshot to write buffer        
    
            #Update snapshot

    #If last seen does not exist or is more than the timeout way

        #Increment the flight numeber for that aircraft

        #Set flag that flight number changed

        #Append the new point to write buffer

        #Update snapshot
    UpdateSnapshot(aircraft, snapshot)
    WritetoFile(aircraft)

    return(1)

#Information in the dump1090 output that is dropped from the data saved to output 
fieldstodrop = ('seen', 'tisb', 'mlat', 'messages', 'rssi', 'track', 'speed', 
                'seen_pos', 'vert_rate', 'nucp', 'category', 'type')

fieldstowrite = ('hex')

#Number of times data is queried
itercnt=0

#Most recent data for each aircraft
#{'hex': {
#         'time': 'string with date last time aircraft was seen', 
#         'flightnum': 'number that increments each time the first seen',
#         'hdglow': 140, 
#         'hdghigh': 141, 
#         'althigh': 0,
#         'altlow': -2,
#         'data': 'raw data from dump1090'}
#}
snapshot = {}

#Data to write to file
writebuffer = ""

#Read config info
jsonurl = "http://10.0.1.53:8080/data/aircraft.json"
outputfileprefix = "dump1090data_"
outputfile = "dump1090data.csv"
lastseenfile = "dump1090lastseen.txt"
logfile = "log.txt"
compalthigh = 500 #feet
compaltlow  = 200 #feet
compheading = 2   #degrees
maxtime =     300 #seconds
snaptimeout = 60  #seconds
pollfreq =    5   #seconds
loglevel =    1   #

#Read lastseen file

WritetoLog(["Starting collection at " + nowstr()])

#Loop forever
while True:
    try:
        
        #print "a"
        #Get data
        itercnt=itercnt+1
        data = getjson(jsonurl)["aircraft"]
        obs=-1

        #Look for new data
        for aircraft in data:
            #print "b"
            obs=obs+1
            removekeysfromdict(fieldstodrop, aircraft)

            #If hex is in snapshot and line is different than snapshot
            if (aircraft["hex"] in snapshot):
                if not(snapshot[aircraft["hex"]]["data"] == aircraft):
                    if loglevel > 5: print aircraft["hex"] + " is in the snapshot but is out of date"   
                    if loglevel > 7: print aircraft["hex"]
                    if loglevel > 7: print snapshot[aircraft["hex"]]["data"]
                    
                    ProcessAircraft(aircraft, snapshot)
                else:
                    if loglevel > 5: print aircraft["hex"] + " is in the snapshot and is current."
                    

            #If aircraft is not already in the snapshot
            if not(aircraft["hex"] in snapshot):
                if loglevel > 5: print aircraft["hex"] + " is not in the snapshot"
                ProcessAircraft(aircraft, snapshot)

            #print aircraft

        #Make a new file if necessary
        #Write to file
        #Clear write buffer

        #If any flight number changed

            #Write flight numbers to file

    except Exception, err:
        print Exception, err
        WritetoLog([Exception, err])
        WritetoLog("Traceback: " + traceback.format_exc())
        pass

    time.sleep(pollfreq)


