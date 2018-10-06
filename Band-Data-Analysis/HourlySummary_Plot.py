# -*- coding: utf-8 -*-
"""
Creates 3 plots from Microsoft Band HOURLY SUMMARY data:
1 - Calories Burned
2 - Steps Taken
3 - Heart Rate (Max, Min, Avg)

Required command line option: filename
Optional command line options: --start StartDate.Hour --end EndDate.Hour

Examples:

Plot the data in DailySummary.txt from April 3rd, 2015 at 2am to July 5th, 2015 at 9pm:
DailySummary_Plot.py DailySummary.txt --start 2015-04-03.02 --end 2015-07-05.18

Plot all data in DailySummary.txt:
DailySummary_Plot.py DailySummary.txt

"""
import json
import re
import matplotlib.pyplot as plt
import seaborn as sea
import datetime as dt
import matplotlib.dates as dates
import argparse
import itertools as it

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="filename which contains Microsoft Band Health data in JSON format")
parser.add_argument("-s", "--start", help="start date/time in the format YYYY-MM-DD.HH")
parser.add_argument("-e", "--end", help="end date/time in the format YYYY-MM-DD.HH")
args = parser.parse_args()

bandDataFile = args.filename
        
# For the few oddball cases where there are missing key/pairs
class chkDict(dict):
    def __missing__(self, key):
        return 0
 
# Clean data for JSON (remove newlines and nextpages)
with open(bandDataFile) as inputfile:
    rawData = ' '.join([line.strip() for line in inputfile])
    rawData = re.sub(r'\],\"nextPage\":\"https:.+?(?=\")\",\"itemCount\":[0-9]*\} \{\"[a-z]*\":\[',r',',rawData.rstrip())
    
# Load our data!
data=json.loads(rawData, object_pairs_hook=chkDict)
       
# Arrays for data that you tend to plot
caloriesBurned = []
avgHeartRate = []
lowHeartRate = []
peakHeartRate = []
stepsTaken = []
dateRange = []

# Pulling out relevant data from the JSON array 
for i in range(0, len(data['summaries'])):
    caloriesBurned.append(data['summaries'][i]['caloriesBurnedSummary']['totalCalories'])
    avgHeartRate.append(data['summaries'][i]['heartRateSummary']['averageHeartRate'])
    lowHeartRate.append(data['summaries'][i]['heartRateSummary']['lowestHeartRate'])
    peakHeartRate.append(data['summaries'][i]['heartRateSummary']['peakHeartRate'])
    stepsTaken.append(data['summaries'][i]['stepsTaken'])
    dateRange.append(re.sub(':\d\d\.\d+[-+]\d\d:\d\d','',data['summaries'][i]['startTime']))

# MS Band timestamp form: 2015-10-31T00:00:00.000-07:00
# Strip everything but the YYYY-MM-DDTHH:MM
x = [dt.datetime.strptime(d,'%Y-%m-%dT%H:%M') for d in dateRange]

if args.start:
    startTime = re.sub('\.{1}','T',args.start)
    startTime+=":00"
    lastIndex = dateRange.index(startTime)
else:
    lastIndex = len(dateRange)  
    
if args.end:
    endTime = re.sub('\.{1}','T',args.end)
    endTime+=":00"
    firstIndex = dateRange.index(endTime)
else:
    firstIndex = 0
    
palette = it.cycle(sea.color_palette())

fig = plt.figure()
sea.set_style('darkgrid')
fig.suptitle('MS Band Hourly Summary',fontsize=16)


ax1 = fig.add_subplot(311)
ax1.plot_date(x[firstIndex:lastIndex],caloriesBurned[firstIndex:lastIndex],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('','Calories Burned')

ax2 = fig.add_subplot(312)                        # 3 rows, 1 column, plot #2
ax2.plot_date(x[firstIndex:lastIndex],stepsTaken[firstIndex:lastIndex],color=next(palette),linestyle='-',fillstyle='none')
sea.axlabel('','Steps Taken')

ax3 = fig.add_subplot(313)                        # 3 rows, 1 column, plot #3
ax3.plot_date(x[firstIndex:lastIndex],avgHeartRate[firstIndex:lastIndex],color=next(palette),linestyle='-',fillstyle='none')
ax3.plot_date(x[firstIndex:lastIndex],lowHeartRate[firstIndex:lastIndex],color=next(palette),linestyle='-',fillstyle='none')
ax3.plot_date(x[firstIndex:lastIndex],peakHeartRate[firstIndex:lastIndex],color=next(palette),linestyle='-',fillstyle='none')
ax3.xaxis.set_major_formatter(dates.DateFormatter('%m/%d/%Y %H:%M'))
fig.autofmt_xdate()               # angle the dates for easier reading
sea.axlabel('Date','Heart Rate')
