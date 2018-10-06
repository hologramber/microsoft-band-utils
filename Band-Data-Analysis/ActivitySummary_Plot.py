# -*- coding: utf-8 -*-
"""
WORK IN PROGRESS!

Creates plots from Microsoft Band ACTIVITY SUMMARY data:

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

parser = argparse.ArgumentParser()
#parser.add_argument("filename", help="filename which contains Microsoft Band Health data in JSON format")
args = parser.parse_args()

#bandDataFile = args.filename
bandDataFile = "GetActBasic.txt"

# For the few oddball cases where there are missing key/pairs, fill in with properly formatted 0s
class chkDict(dict):
    def __missing__(self, key):
        match = re.search(r'uration', key)
        matchtime = re.search(r'Time', key)
        if match:
            return 'PT0M0S'
        if matchtime:
            return '0000-00-00T00:00:00.000+00:00'
        else:
            return 0

# Clean data for JSON (remove newlines and nextpages)
with open(bandDataFile) as inputfile:
    rawData = ' '.join([line.strip() for line in inputfile])
    rawData = re.sub(r',\"nextPage\":\"https:.+?(?=\")\",\"itemCount\":[0-9]*\} \{',r',',rawData.rstrip())
    
countFixRun = it.count()
countFixBike =  it.count()
countFixSleep = it.count()
countFixGolf = it.count()
countFixGWo = it.count()
countFixFWo = it.count()
rawData = re.sub(r'bikeActivities', lambda x: 'bikeActivities{{{}}}'.format(next(countFixBike)),rawData)
rawData = re.sub(r'runActivities', lambda x: 'runActivities{{{}}}'.format(next(countFixRun)),rawData)
rawData = re.sub(r'sleepActivities', lambda x: 'sleepActivities{{{}}}'.format(next(countFixSleep)),rawData)
rawData = re.sub(r'golfActivities', lambda x: 'golfActivities{{{}}}'.format(next(countFixGolf)),rawData)
rawData = re.sub(r'guidedWorkoutActivities', lambda x: 'guidedWorkoutActivities{{{}}}'.format(next(countFixGWo)),rawData)
rawData = re.sub(r'freePlayActivities', lambda x: 'freePlayActivities{{{}}}'.format(next(countFixFWo)),rawData)

# Load our data!
data=json.loads(rawData, object_pairs_hook=chkDict)


# -------------------------------------------------
# BICYCLING ACTIVITY DATA
# -------------------------------------------------
activityDateB = []
caloriesBurnedB = []
avgHeartRateB = []
lowHeartRateB = []
peakHeartRateB = []
zoneHeartRateB = []
totalDistanceB = []
actDurationB = []

# Pulling out relevant data from the JSON array 
for i1 in range(0,next(countFixBike)):
    for i in range(0, len(data['bikeActivities{'+str(i1)+'}'])):
        activityDateB.append(re.sub('T.*','',data['bikeActivities{'+str(i1)+'}'][i]['startTime']))
        caloriesBurnedB.append(data['bikeActivities{'+str(i1)+'}'][i]['caloriesBurnedSummary']['totalCalories'])
        totalDistanceB.append(data['bikeActivities{'+str(i1)+'}'][i]['distanceSummary']['totalDistance'])
        actDurationB.append(((isodate.parse_duration(data['bikeActivities{'+str(i1)+'}'][i]['duration'])).total_seconds())/60/60)
        avgHeartRateB.append(data['bikeActivities{'+str(i1)+'}'][i]['heartRateSummary']['averageHeartRate'])
        lowHeartRateB.append(data['bikeActivities{'+str(i1)+'}'][i]['heartRateSummary']['lowestHeartRate'])
        peakHeartRateB.append(data['bikeActivities{'+str(i1)+'}'][i]['heartRateSummary']['peakHeartRate'])
        zoneHeartRateB.append(data['bikeActivities{'+str(i1)+'}'][i]['performanceSummary']['heartRateZones'])

xB = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in activityDateB]

#if args.start:
#    startTime = args.start
#    lastIndex = dateRange.index(startTime)
#else:
lastIndexB = len(activityDateB)  
    
#if args.end:
#    endTime = args.end
#    firstIndex = dateRange.index(endTime)
#else:
firstIndexB = 0

paletteB = it.cycle(sea.color_palette())
    
fig = plt.figure()
fig.suptitle('MS Band Bike Summary',fontsize=16)
sea.set_style('darkgrid')

ax1 = fig.add_subplot(221)              # 2 rows, 2 columns, top left
ax1.plot_date(xB[firstIndexB:lastIndexB],actDurationB[firstIndexB:lastIndexB],color=next(paletteB))    
sea.axlabel('','Activity Duration')

ax2 = fig.add_subplot(222)              # 2 rows, 2 columns, top right
ax2.plot_date(xB[firstIndexB:lastIndexB],caloriesBurnedB[firstIndexB:lastIndexB],color=next(paletteB))    
sea.axlabel('','Calories Burned')

ax3 = fig.add_subplot(223)              # 2 rows, 2 columns, bottom left
ax3.plot_date(xB[firstIndexB:lastIndexB],totalDistanceB[firstIndexB:lastIndexB],color=next(paletteB))
ax3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig.autofmt_xdate()               # angle the dates for easier reading      
sea.axlabel('Date','Total Distance')

ax4 = fig.add_subplot(224)              # 2 rows, 2 columns, bottom right
ax4.plot_date(xB[firstIndexB:lastIndexB],avgHeartRateB[firstIndexB:lastIndexB],color=next(paletteB))
ax4.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig.autofmt_xdate()               # angle the dates for easier reading
sea.axlabel('Date','Heart Rate')


# -------------------------------------------------
# GUIDED WORKOUT ACTIVITY DATA
# -------------------------------------------------
activityDateWG = []
caloriesBurnedWG = []
avgHeartRateWG = []
lowHeartRateWG = []
peakHeartRateWG = []
zoneHeartRateWG = []
actDurationWG = []
workoutIDWG = []

for j1 in range(0,next(countFixGWo)):
    for j in range(0, len(data['guidedWorkoutActivities{'+str(j1)+'}'])):
        activityDateWG.append(re.sub('T.*','',data['guidedWorkoutActivities{'+str(j1)+'}'][j]['startTime']))
        caloriesBurnedWG.append(data['guidedWorkoutActivities{'+str(j1)+'}'][j]['caloriesBurnedSummary']['totalCalories'])
        actDurationWG.append(((isodate.parse_duration(data['guidedWorkoutActivities{'+str(j1)+'}'][j]['duration'])).total_seconds())/60)
        avgHeartRateWG.append(data['guidedWorkoutActivities{'+str(j1)+'}'][j]['heartRateSummary']['averageHeartRate'])
        lowHeartRateWG.append(data['guidedWorkoutActivities{'+str(j1)+'}'][j]['heartRateSummary']['lowestHeartRate'])
        peakHeartRateWG.append(data['guidedWorkoutActivities{'+str(j1)+'}'][j]['heartRateSummary']['peakHeartRate'])
        zoneHeartRateWG.append(data['guidedWorkoutActivities{'+str(j1)+'}'][j]['performanceSummary']['heartRateZones'])
        workoutIDWG.append(data['guidedWorkoutActivities{'+str(j1)+'}'][j]['workoutPlanId'])

xWG = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in activityDateWG]

#    startTime = args.start
#    lastIndex = dateRange.index(startTime)
#else:
lastIndexWG = len(activityDateWG)  
    
#if args.end:
#    endTime = args.end
#    firstIndex = dateRange.index(endTime)
#else:
firstIndexWG = 0

paletteWG = it.cycle(sea.color_palette())
    
fig2 = plt.figure()
fig2.suptitle('MS Band Guided Workout Summary',fontsize=16)
sea.set_style('darkgrid')

ax_wo1 = fig2.add_subplot(311)
ax_wo1.plot_date(xWG[firstIndexWG:lastIndexWG],actDurationWG[firstIndexWG:lastIndexWG],color=next(paletteWG))
sea.axlabel('','Workout Duration')

ax_wo2 = fig2.add_subplot(312)
ax_wo2.plot_date(xWG[firstIndexWG:lastIndexWG],caloriesBurnedWG[firstIndexWG:lastIndexWG],color=next(paletteWG))
sea.axlabel('','Calories Burned')

ax_wo3 = fig2.add_subplot(313)                        
ax_wo3.plot_date(xWG[firstIndexWG:lastIndexWG],avgHeartRateWG[firstIndexWG:lastIndexWG],color=next(paletteWG))
ax_wo3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig2.autofmt_xdate()               # angle the dates for easier reading
sea.axlabel('Date','Heart Rate')

# -------------------------------------------------
# RUNNING ACTIVITY DATA
# -------------------------------------------------
activityDateR = []
caloriesBurnedR = []
avgHeartRateR = []
lowHeartRateR = []
peakHeartRateR = []
zoneHeartRateR = []
totalDistanceR = []
actDurationR = []
runningPaceR = []

for k1 in range(0,next(countFixRun)):
    for k in range(0, len(data['runActivities{'+str(k1)+'}'])):
        activityDateR.append(re.sub('T.*','',data['runActivities{'+str(k1)+'}'][k]['startTime']))
        caloriesBurnedR.append(data['runActivities{'+str(k1)+'}'][k]['caloriesBurnedSummary']['totalCalories'])
        totalDistanceR.append(data['runActivities{'+str(k1)+'}'][k]['distanceSummary']['totalDistance'])
        actDurationR.append(((isodate.parse_duration(data['runActivities{'+str(k1)+'}'][k]['duration'])).total_seconds())/60/60)
        avgHeartRateR.append(data['runActivities{'+str(k1)+'}'][k]['heartRateSummary']['averageHeartRate'])
        lowHeartRateR.append(data['runActivities{'+str(k1)+'}'][k]['heartRateSummary']['lowestHeartRate'])
        peakHeartRateR.append(data['runActivities{'+str(k1)+'}'][k]['heartRateSummary']['peakHeartRate'])
        zoneHeartRateR.append(data['runActivities{'+str(k1)+'}'][k]['performanceSummary']['heartRateZones'])
        runningPaceR.append(data['runActivities{'+str(k1)+'}'][k]['distanceSummary']['pace'])

xR = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in activityDateR]

lastIndexR = len(activityDateR)  
firstIndexR = 0

paletteR = it.cycle(sea.color_palette())

fig3 = plt.figure()
fig3.suptitle('MS Band Run Summary',fontsize=16)
sea.set_style('darkgrid')

ax_r1 = fig3.add_subplot(221)
ax_r1.plot_date(xR[firstIndexR:lastIndexR],actDurationR[firstIndexR:lastIndexR],color=next(paletteR))
sea.axlabel('','Run Duration')

ax_r2 = fig3.add_subplot(222)
ax_r2.plot_date(xR[firstIndexR:lastIndexR],caloriesBurnedR[firstIndexR:lastIndexR],color=next(paletteR))
sea.axlabel('','Calories Burned')

ax_r3 = fig3.add_subplot(223)
ax_r3.plot_date(xR[firstIndexR:lastIndexR],totalDistanceR[firstIndexR:lastIndexR],color=next(paletteR))
ax_r3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig3.autofmt_xdate()               # angle the dates for easier reading
sea.axlabel('Date','Run Distance')

ax_r4 = fig3.add_subplot(224)
ax_r4.plot_date(xR[firstIndexR:lastIndexR],avgHeartRateR[firstIndexR:lastIndexR],color=next(paletteR))
ax_r4.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig3.autofmt_xdate()               # angle the dates for easier reading
sea.axlabel('Date','Heart Rate')

# -------------------------------------------------
# FREE WORKOUT ACTIVITY DATA
# -------------------------------------------------
activityDateFW = []
caloriesBurnedFW = []
avgHeartRateFW = []
lowHeartRateFW = []
peakHeartRateFW = []
zoneHeartRateFW = []
actDurationFW = []

for n1 in range(0,next(countFixFWo)):
    for n in range(0, len(data['freePlayActivities{'+str(n1)+'}'])):
        activityDateFW.append(re.sub('T.*','',data['freePlayActivities{'+str(n1)+'}'][n]['startTime']))
        caloriesBurnedFW.append(data['freePlayActivities{'+str(n1)+'}'][n]['caloriesBurnedSummary']['totalCalories'])
        actDurationFW.append(((isodate.parse_duration(data['freePlayActivities{'+str(n1)+'}'][n]['duration'])).total_seconds())/60)
        avgHeartRateFW.append(data['freePlayActivities{'+str(n1)+'}'][n]['heartRateSummary']['averageHeartRate'])
        lowHeartRateFW.append(data['freePlayActivities{'+str(n1)+'}'][n]['heartRateSummary']['lowestHeartRate'])
        peakHeartRateFW.append(data['freePlayActivities{'+str(n1)+'}'][n]['heartRateSummary']['peakHeartRate'])
        zoneHeartRateFW.append(data['freePlayActivities{'+str(n1)+'}'][n]['performanceSummary']['heartRateZones'])

xFW = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in activityDateFW]

lastIndexFW = len(activityDateFW)  
firstIndexFW = 0

paletteFW = it.cycle(sea.color_palette())

fig4 = plt.figure()
fig4.suptitle('MS Band Free Workout Summary',fontsize=16)    
sea.set_style('darkgrid')

ax_fw1 = fig4.add_subplot(311)                        # 3 rows, 1 column, plot #1
ax_fw1.plot_date(xFW[firstIndexFW:lastIndexFW],actDurationFW[firstIndexFW:lastIndexFW],color=next(paletteFW))
sea.axlabel('','Workout Duration')

ax_fw2 = fig4.add_subplot(312)
ax_fw2.plot_date(xFW[firstIndexFW:lastIndexFW],caloriesBurnedFW[firstIndexFW:lastIndexFW],color=next(paletteFW))
sea.axlabel('','Calories Burned')

ax_fw3 = fig4.add_subplot(313)                        # 3 rows, 1 column, plot #3
ax_fw3.plot_date(xFW[firstIndexFW:lastIndexFW],avgHeartRateFW[firstIndexFW:lastIndexFW],color=next(paletteFW))
ax_fw3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig4.autofmt_xdate()               # angle the dates for easier reading
sea.axlabel('Date','Heart Rate')


'''    
# -------------------------------------------------
# GOLF ACTIVITY DATA
# -------------------------------------------------
activityDateG = []
caloriesBurnedG = []
actDurationG = []
totalDistanceG = []
golfParOrBetter = []
for p1 in range(0,next(countFixGolf)):
    for p in range(0, len(data['golfActivities{'+str(p1)+'}'])):
        activityDateG.append(re.sub('T.*','',data['golfActivities{'+str(p1)+'}'][i]['startTime']))
        caloriesBurnedG.append(data['golfActivities{'+str(p1)+'}'][i]['caloriesBurnedSummary']['totalCalories'])
        actDurationG.append(((isodate.parse_duration(data['golfActivities{'+str(p1)+'}'][i]['duration'])).total_seconds())/60/60)
        totalDistanceG.append(data['golfActivities{'+str(p1)+'}'][i]['totalDistanceWalked'])
        golfParOrBetter.append(data['golfActivities{'+str(p1)+'}'][i]['parOrBetterCount'])

# Sorry.. I have no golf activities, but creating a plot should be easy enough if you template from other activities.
'''

# -------------------------------------------------
# SLEEP ACTIVITY DATA
# -------------------------------------------------
activityDateS = []
caloriesBurnedS = []
actDurationS = []
avgHeartRateS = []
lowHeartRateS = []
peakHeartRateS = []
sleepNumWakeup = []
fallAsleepTime = []
wakeupTime = []
sleepEfficiency = []
restfulSleep = []
restlessSleep = []
awakeDuration = []
sleepDuration = []
fallAsleepDuration = []

for m1 in range(0,next(countFixSleep)):
    for m in range(0, len(data['sleepActivities{'+str(m1)+'}'])):
        activityDateS.append(re.sub('T.*','',data['sleepActivities{'+str(m1)+'}'][m]['startTime']))
        caloriesBurnedS.append(data['sleepActivities{'+str(m1)+'}'][m]['caloriesBurnedSummary']['totalCalories'])
        sleepDuration.append(((isodate.parse_duration(data['sleepActivities{'+str(m1)+'}'][m]['sleepDuration'])).total_seconds())/60/60)
        actDurationS.append(((isodate.parse_duration(data['sleepActivities{'+str(m1)+'}'][m]['duration'])).total_seconds())/60/60)
        avgHeartRateS.append(data['sleepActivities{'+str(m1)+'}'][m]['heartRateSummary']['averageHeartRate'])
        lowHeartRateS.append(data['sleepActivities{'+str(m1)+'}'][m]['heartRateSummary']['lowestHeartRate'])
        peakHeartRateS.append(data['sleepActivities{'+str(m1)+'}'][m]['heartRateSummary']['peakHeartRate'])
        sleepNumWakeup.append(data['sleepActivities{'+str(m1)+'}'][m]['numberOfWakeups'])
        #pprint(data['sleepActivities{'+str(m1)+'}'][m]['fallAsleepTime'])
        fallAsleepTime.append((((int(data['sleepActivities{'+str(m1)+'}'][m]['fallAsleepTime'][11:13]))*60)+(int(data['sleepActivities{'+str(m1)+'}'][m]['fallAsleepTime'][14:16])))/60)
        #fallAsleepTime.append(data['sleepActivities{'+str(m1)+'}'][m]['fallAsleepTime'])
        wakeupTime.append((((int(data['sleepActivities{'+str(m1)+'}'][m]['wakeupTime'][11:13]))*60)+(int(data['sleepActivities{'+str(m1)+'}'][m]['wakeupTime'][14:16])))/60)
        #wakeupTime.append(data['sleepActivities{'+str(m1)+'}'][m]['wakeupTime'])
        sleepEfficiency.append(data['sleepActivities{'+str(m1)+'}'][m]['sleepEfficiencyPercentage'])
        restfulSleep.append(((isodate.parse_duration(data['sleepActivities{'+str(m1)+'}'][m]['totalRestfulSleepDuration'])).total_seconds())/60/60)
        restlessSleep.append(((isodate.parse_duration(data['sleepActivities{'+str(m1)+'}'][m]['totalRestlessSleepDuration'])).total_seconds())/60/60)
        awakeDuration.append(((isodate.parse_duration(data['sleepActivities{'+str(m1)+'}'][m]['awakeDuration'])).total_seconds())/60/60)
        fallAsleepDuration.append(((isodate.parse_duration(data['sleepActivities{'+str(m1)+'}'][m]['fallAsleepDuration'])).total_seconds())/60/60)

xS = [dt.datetime.strptime(d,'%Y-%m-%d').date() for d in activityDateS]

lastIndexS = len(activityDateS)  
firstIndexS = 0

# SLEEP PLOT #1 (Total Duration, Time to Sleep, Sleep Duration, Restless, Restful, Awake Duration)
palette = it.cycle(sea.color_palette())
fig5 = plt.figure()
fig5.suptitle('MS Band Sleep Summary 1',fontsize=16)
sea.set_style('darkgrid')

ax_s1 = fig5.add_subplot(321)                       
ax_s1.plot_date(xS[firstIndexS:lastIndexS],actDurationS[firstIndexS:lastIndexS],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('','Total Duration')

ax_s2 = fig5.add_subplot(322)                       
ax_s2.plot_date(xS[firstIndexS:lastIndexS],fallAsleepDuration[firstIndexS:lastIndexS],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('','Time to Fall Asleep')

ax_s3 = fig5.add_subplot(323)                       
ax_s3.plot_date(xS[firstIndexS:lastIndexS],sleepDuration[firstIndexS:lastIndexS],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('','Sleep Duration')

ax_s4 = fig5.add_subplot(324)                       
ax_s4.plot_date(xS[firstIndexS:lastIndexS],restlessSleep[firstIndexS:lastIndexS],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('','Restless Sleep')

ax_s5 = fig5.add_subplot(325)                       
ax_s5.plot_date(xS[firstIndexS:lastIndexS],awakeDuration[firstIndexS:lastIndexS],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('Date','Awake Duration')
ax_s5.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig5.autofmt_xdate()               # angle the dates for easier reading

ax_s6 = fig5.add_subplot(326)                       
ax_s6.plot_date(xS[firstIndexS:lastIndexS],restfulSleep[firstIndexS:lastIndexS],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('Date','Restful Sleep')
ax_s6.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y'))
fig5.autofmt_xdate()               # angle the dates for easier reading

# SLEEP PLOT #2 (Calories, Hour Asleep, Hour Awake, HR, # Times Awake, Efficiency)
palette2 = it.cycle(sea.color_palette())
fig6 = plt.figure()
fig6.suptitle('MS Band Sleep Summary 2',fontsize=16)
sea.set_style('darkgrid')

ax_sx1 = fig6.add_subplot(321)
ax_sx1.plot_date(xS[firstIndexS:lastIndexS],caloriesBurnedS[firstIndexS:lastIndexS],color=next(palette2),linestyle='-',fillstyle='none')
sea.axlabel('','Calories Burned')

ax_sx2 = fig6.add_subplot(322)
ax_sx2.plot_date(xS[firstIndexS:lastIndexS],fallAsleepTime[firstIndexS:lastIndexS],color=next(palette2),linestyle='-',fillstyle='none')
sea.axlabel('','GMT Hour Asleep')

ax_sx3 = fig6.add_subplot(323)                      
ax_sx3.plot_date(xS[firstIndexS:lastIndexS],lowHeartRateS[firstIndexS:lastIndexS],color=next(palette2),linestyle='-',fillstyle='none')
sea.axlabel('','L Heart Rate')

ax_sx4 = fig6.add_subplot(324)
ax_sx4.plot_date(xS[firstIndexS:lastIndexS],wakeupTime[firstIndexS:lastIndexS],color=next(palette2),linestyle='-',fillstyle='none')
sea.axlabel('','GMT Hour Awake')

ax_sx5 = fig6.add_subplot(325)
ax_sx5.plot_date(xS[firstIndexS:lastIndexS],sleepNumWakeup[firstIndexS:lastIndexS],color=next(palette2),linestyle='-',fillstyle='none')
sea.axlabel('Date','# of Times Awake')

ax_sx6 = fig6.add_subplot(326)
ax_sx6.plot_date(xS[firstIndexS:lastIndexS],sleepEfficiency[firstIndexS:lastIndexS],color=next(palette2),linestyle='-',fillstyle='none')
sea.axlabel('Date','% Sleep Efficiency')