# -*- coding: utf-8 -*-
"""
Converts the Microsoft Band GPS data to the open GPX format.

WORK IN PROGRESS

"""

import json
from pprint import pprint
import re
import matplotlib.pyplot as plt
import seaborn as sea
import datetime as dt
import matplotlib.dates as dates
import argparse
import isodate
import itertools as it

bandDataFile = 'GetActGPS.txt'
activityType = 'Running'

# For the few oddball cases where there are missing key/pairs, fill in with properly formatted 0s
class chkDict(dict):
    def __missing__(self, key):
        match = re.search(r'uration', key)
        matchtime = re.search(r'Time', key)
        matchgps = re.search(r'location', key)
        if match:
            return 'PT0M0S'
        if matchtime:
            return '0000-00-00T00:00:00.000+00:00'
        if matchgps:
            return {"latitude":0,"longitude":0,"elevationFromMeanSeaLevel":0}
        else:
            return 0

# Clean data for JSON (remove newlines and nextpages)
with open(bandDataFile) as inputfile:
    rawData = ' '.join([line.strip() for line in inputfile])
    rawData = re.sub(r',\"nextPage\":\"https:.+?(?=\")\",\"itemCount\":[0-9]*\} \{',r',',rawData.rstrip())
    
countFixRun = it.count()
countFixBike =  it.count()
countFixGolf = it.count()
rawData = re.sub(r'bikeActivities', lambda x: 'bikeActivities{{{}}}'.format(next(countFixBike)),rawData)
rawData = re.sub(r'runActivities', lambda x: 'runActivities{{{}}}'.format(next(countFixRun)),rawData)
rawData = re.sub(r'golfActivities', lambda x: 'golfActivities{{{}}}'.format(next(countFixGolf)),rawData)

# Load our data!
data=json.loads(rawData, object_pairs_hook=chkDict)

headerString = '<?xml version="1.0" encoding="UTF-8"?>\n<gpx\n\tversion="1.1"\n\tcreator="BandSandbox apps@dendriticspine.com"\n\t\
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n\txmlns="http://www.topografix.com/GPX/1/1"\n\t\
xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"\n\t\
xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1">\n<trk>\n'

endingString = '</trkseg>\n</trk>\n</gpx>\n'

gpsData = []
activityStart = []
activityStartStr = []
speedData = []
gpsTimeCalc = []
mapPointType = []
heartRatePoint = []
pointLat = []
pointLong = []
pointEle = []

# -------------------------------------------------
# BICYCLING ACTIVITY DATA
# -------------------------------------------------
if (activityType == 'Cycling'):
    # Pulling out relevant data from the JSON array 
    for i1 in range(0,next(countFixBike)):
        for i in range(0, len(data['bikeActivities{'+str(i1)+'}'])):
            currStartTime = re.sub('.\d+[-+]\d\d:\d\d','',data['bikeActivities{'+str(i1)+'}'][i]['startTime'])
            dtStartTime = dt.datetime.strptime(currStartTime, '%Y-%m-%dT%H:%M:%S')
            activityStart.append(dtStartTime.strftime('%Y-%m-%dT%H:%M:%SZ'))
            activityStartStr.append(dtStartTime.strftime('%Y-%m-%d-%H-%M-%S'))
            for igps in range(0,len(data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'])):
                mapPointType.append(data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['mapPointType'])
                secSinceStart = data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['secondsSinceStart']
                gpsTimeCalcTemp = dtStartTime + dt.timedelta(seconds=secSinceStart)
                gpsTimeCalc.append(gpsTimeCalcTemp.strftime('%Y-%m-%dT%H:%M:%SZ'))
                heartRatePoint.append(data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['heartRate'])
                speedData.append(data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['speed'])
                pointLat.append(data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['latitude'])
                pointLong.append(data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['longitude'])
                pointEle.append(data['bikeActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['elevationFromMeanSeaLevel'])
            gpsData.append([pointLat, pointLong, pointEle, mapPointType, gpsTimeCalc, speedData, heartRatePoint])
            speedData = []
            gpsTimeCalc = []
            mapPointType = []
            heartRatePoint = []
            pointLat = []
            pointLong = []
            pointEle = []
    
# -------------------------------------------------
# RUNNING ACTIVITY DATA
# -------------------------------------------------
if (activityType == 'Running'):
    # Pulling out relevant data from the JSON array 
    for i1 in range(0,next(countFixRun)):
        for i in range(0, len(data['runActivities{'+str(i1)+'}'])):
            currStartTime = re.sub('.\d+[-+]\d\d:\d\d','',data['runActivities{'+str(i1)+'}'][i]['startTime'])
            dtStartTime = dt.datetime.strptime(currStartTime, '%Y-%m-%dT%H:%M:%S')
            activityStart.append(dtStartTime.strftime('%Y-%m-%dT%H:%M:%SZ'))
            activityStartStr.append(dtStartTime.strftime('%Y-%m-%d-%H-%M-%S'))
            for igps in range(0,len(data['runActivities{'+str(i1)+'}'][i]['mapPoints'])):
                mapPointType.append(data['runActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['mapPointType'])
                secSinceStart = data['runActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['secondsSinceStart']
                gpsTimeCalcTemp = dtStartTime + dt.timedelta(seconds=secSinceStart)
                gpsTimeCalc.append(gpsTimeCalcTemp.strftime('%Y-%m-%dT%H:%M:%SZ'))
                heartRatePoint.append(data['runActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['heartRate'])
                speedData.append(data['runActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['speed'])
                pointLat.append(data['runActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['latitude'])
                pointLong.append(data['runActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['longitude'])
                pointEle.append(data['runActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['elevationFromMeanSeaLevel'])
            gpsData.append([pointLat, pointLong, pointEle, mapPointType, gpsTimeCalc, speedData, heartRatePoint])
            speedData = []
            gpsTimeCalc = []
            mapPointType = []
            heartRatePoint = []
            pointLat = []
            pointLong = []
            pointEle = []

# -------------------------------------------------
# GOLF ACTIVITY DATA
# -------------------------------------------------
if (activityType == 'Golf'):
    # Pulling out relevant data from the JSON array 
    for i1 in range(0,next(countFixGolf)):
        for i in range(0, len(data['golfActivities{'+str(i1)+'}'])):
            currStartTime = re.sub('.\d+[-+]\d\d:\d\d','',data['golfActivities{'+str(i1)+'}'][i]['startTime'])
            dtStartTime = dt.datetime.strptime(currStartTime, '%Y-%m-%dT%H:%M:%S')
            activityStart.append(dtStartTime.strftime('%Y-%m-%dT%H:%M:%SZ'))
            activityStartStr.append(dtStartTime.strftime('%Y-%m-%d-%H-%M-%S'))
            for igps in range(0,len(data['golfActivities{'+str(i1)+'}'][i]['mapPoints'])):
                mapPointType.append(data['golfActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['mapPointType'])
                secSinceStart = data['golfActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['secondsSinceStart']
                gpsTimeCalcTemp = dtStartTime + dt.timedelta(seconds=secSinceStart)
                gpsTimeCalc.append(gpsTimeCalcTemp.strftime('%Y-%m-%dT%H:%M:%SZ'))
                heartRatePoint.append(data['golfActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['heartRate'])
                speedData.append(data['golfActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['speed'])
                pointLat.append(data['golfActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['latitude'])
                pointLong.append(data['golfActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['longitude'])
                pointEle.append(data['golfActivities{'+str(i1)+'}'][i]['mapPoints'][igps]['location']['elevationFromMeanSeaLevel'])
            gpsData.append([pointLat, pointLong, pointEle, mapPointType, gpsTimeCalc, speedData, heartRatePoint])
            speedData = []
            gpsTimeCalc = []
            mapPointType = []
            heartRatePoint = []
            pointLat = []
            pointLong = []
            pointEle = []
            
                    
for p in range(0,len(activityStart)):
    fileNameString = activityType + '_' + activityStartStr[p] + '.gpx'
    f = open(fileNameString, 'w')
    f.write(headerString)

    nameTimeString = '<name><![CDATA[{0} {1}]]></name><time>{1}</time>\n\n<trkseg>\n'.format(activityType, activityStart[p])
    f.write(nameTimeString)
    
    for q in range(0,len(gpsData[p][0])):
        gpsPointString = '<trkpt lat="{0}" lon="{1}"><ele>{2}</ele><name>{3}</name><time>{4}</time><speed>{5}</speed><desc>{6}</desc></trkpt>\n'.format(gpsData[p][0][q],gpsData[p][1][q],gpsData[p][2][q],gpsData[p][3][q],gpsData[p][4][q],gpsData[p][5][q],gpsData[p][6][q])
        f.write(gpsPointString)
        
    f.write(endingString)
    f.close()