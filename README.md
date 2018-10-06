# Band-Data-Analysis
Python scripts for analyzing/visualizing data acquired with the Microsoft Band (and downloaded via the Microsoft Health API).

Download your data: https://github.com/kairozu/Microsoft-Band-Utils/tree/master/BandSandbox-Data-Extract

Microsoft Health API: https://developer.microsoftband.com/cloudAPI

# BandSandbox-Data-Extract
Simple WPF app which uses the MS Health Cloud API to download user-specified data sets acquired with the Microsoft Band. 

Information on using the Microsoft Health Cloud API:
https://developer.microsoftband.com/cloudAPI

Note: The code is ugly. I mean, really, really ugly.

To get started: download visual studio community, import the solution (.sln) file, go to the project properties window (right-click the project node in the Solution Explorer and select Properties), click the "signing" tab and create your own certificate (otherwise you'll receive an error about not being able to locate the .pfx file), insert your own ClientId and ClientSecret in MainWindow.xaml.cs, and build/run the BandSandbox project.

Time for requesting 1 year+5 days (572 activities) worth of...
- Hourly Summary Data: 8 min, 31 sec
- Daily Summary Data: 28 sec
- All Activities: Basic Activity Summary Data: 19 sec
- All Activities: GPS Data & Segment Details: 6 min, 34 sec
- All Activities: Minute Interval Summaries: 18 min, 42 sec (this required additional delays between requests to avoid being throttled for going over the bandwidth limits)

Updates:
- 2015/11/01: The beginnings of some rough Python scripts for plotting Daily Summary, Hourly Summary, and Activity Summary data are here: https://github.com/kairozu/Microsoft-Band-Utils/tree/master/Band-Data-Analysis
- 2015/11/06: Added rate limiting to avoid being throttled by MS health cloud for too many requests/too much bandwidth.
- 2017/08/06: Updated the range of possible dates to include 2017-2019.
- 2017/09/01: Fixed date processing; thanks to Pru for helping me debug. :)