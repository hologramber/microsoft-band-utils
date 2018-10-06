using System;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.IO;
using System.Net;
using System.Text.RegularExpressions;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Navigation;

using Newtonsoft.Json.Linq;
using Microsoft.Win32;

namespace BandSandbox {
    // everything that talks to MainWindow.xaml
    public partial class MainWindow : Window {
        public MainWindow() {
            InitializeComponent();
        }

        private LiveIdCredentials creds = new LiveIdCredentials();

        // ClientId and ClientSecret obtained from: https://account.live.com/developers/applications
        // create app > change "mobile or desktop client app" to yes > c/p from app settings
        private const string ClientId = "replace-with-your-own-application-id";
        private const string ClientSecret ="replace-with-your-own-client-secret";

        // minimum set of authorization scopes
        private const string Scopes = "mshealth.ReadProfile mshealth.ReadActivityHistory mshealth.ReadActivityLocation mshealth.ReadDevices";
        private const string BaseHealthUri = "https://api.microsofthealth.net/v1/me/";
        private const string RedirectUri = "https://login.live.com/oauth20_desktop.srf";

        // global variables for dates/authentication
        private string userStartDate;
        private string userEndDate;
        private bool userAuthenticated = false;
        private int todayMonth = DateTime.Now.Month;
        private int todayDay = DateTime.Now.Day;
        private int todayYear = DateTime.Now.Year;
        private int secDelayRequest = 6;
        private string saveFilePath = "";
        private DateTime startDateDT;
        private DateTime endDateDT;
        private DateTime earliestDT = new DateTime(2014, 10, 29);

        #region API requests

        // update user-entered start date
        private void optionStartDateChanged(object sender, SelectionChangedEventArgs e) {
            int startMonth = this.selStartMonth.SelectedIndex + 1;
            int startDay = this.selStartDay.SelectedIndex + 1;
            int startYear = this.selStartYear.SelectedIndex + 2014;
            string newStart = startYear + "," + startMonth + "," + startDay;

            if (DateTime.TryParse(newStart, out startDateDT)) {
                this.userStartDate = startDateDT.ToString("O");
            } 
        }

        // update user-entered end date
        private void optionEndDateChanged(object sender, SelectionChangedEventArgs e) {
            int endMonth = this.selEndMonth.SelectedIndex + 1;
            int endDay = this.selEndDay.SelectedIndex + 1;
            int endYear = this.selEndYear.SelectedIndex + 2014;
            string newEnd = endYear + "," + endMonth + "," + endDay;

            if (DateTime.TryParse(newEnd, out endDateDT)) {
                this.userEndDate = endDateDT.ToString("O");
            }
        }

        // disable user-dates and run from oct 30, 2014 - today
        private void optionCompleteHistory(object sender, RoutedEventArgs e) {
            if (completeHistoryOpt.IsChecked == true) {
                this.selStartMonth.SelectedIndex = 9;
                this.selStartDay.SelectedIndex = 29;
                this.selStartYear.SelectedIndex = 0;
                this.selStartMonth.Foreground = new SolidColorBrush(Colors.Gray);
                this.selStartDay.Foreground = new SolidColorBrush(Colors.Gray);
                this.selStartYear.Foreground = new SolidColorBrush(Colors.Gray);
                this.selStartMonth.IsEnabled = false;
                this.selStartDay.IsEnabled = false;
                this.selStartYear.IsEnabled = false;

                this.selEndMonth.SelectedIndex = this.todayMonth - 1;
                this.selEndDay.SelectedIndex = this.todayDay - 1;
                this.selEndYear.SelectedIndex = this.todayYear - 2014;
                this.selEndMonth.Foreground = new SolidColorBrush(Colors.Gray);
                this.selEndDay.Foreground = new SolidColorBrush(Colors.Gray);
                this.selEndYear.Foreground = new SolidColorBrush(Colors.Gray);
                this.selEndMonth.IsEnabled = false;
                this.selEndDay.IsEnabled = false;
                this.selEndYear.IsEnabled = false;

                this.userStartDate = "2014-10-30T00:00:01Z";
                this.userEndDate = DateTime.Now.ToString("O");                
                this.statusBar.Text = "Start date set to 10/30/2014, when the MS Band 1 went on sale -- theoretically the earliest day that band data should be available.";
            } else {
                this.selStartMonth.IsEnabled = true;
                this.selStartDay.IsEnabled = true;
                this.selStartYear.IsEnabled = true;
                this.selStartMonth.Foreground = new SolidColorBrush(Colors.Black);
                this.selStartDay.Foreground = new SolidColorBrush(Colors.Black);
                this.selStartYear.Foreground = new SolidColorBrush(Colors.Black);

                this.selEndMonth.IsEnabled = true;
                this.selEndDay.IsEnabled = true;
                this.selEndYear.IsEnabled = true;
                this.selEndMonth.Foreground = new SolidColorBrush(Colors.Black);
                this.selEndDay.Foreground = new SolidColorBrush(Colors.Black);
                this.selEndYear.Foreground = new SolidColorBrush(Colors.Black);

                this.statusBar.Text = "Please select appropriate start/end dates.";
            }
        }

        // download ms health cloud profile data
        private async void getProfileButton_Click(object sender, RoutedEventArgs e) {
            this.statusBar.Text = "Requesting data from MS Health Cloud...";
            await this.PerformRequest("Profile");
        }

        // download ms health cloud devices data
        private async void getDevicesButton_Click(object sender, RoutedEventArgs e) {
            this.statusBar.Text = "Requesting data from MS Health Cloud...";
            await this.PerformRequest("Devices");
        }

        // TODO validate date entries
        private bool validateDates() {
            if (startDateDT > endDateDT) {
                this.statusBar.Text = "Please adjust your dates -- the start date occurs after the end date.";
                return false;
            } else if (endDateDT > DateTime.Now) {
                this.statusBar.Text = "Please adjust your dates -- your end date can't be in the future.";
                return false;
            } else if (startDateDT < earliestDT) {
                this.statusBar.Text = "Please adjust your dates -- earliest start date is October 30, 2014.";
                return false;
            }
            return true;
        }

        // get daily summary data
        private async void getDailySummaryButton_Click(object sender, RoutedEventArgs e) {
            if (this.validateDates()) {
                this.secDelayRequest = 2;
                this.statusBar.Text = "Requesting data from MS Health Cloud...";
                await this.PerformRequest("Summaries/Daily", string.Format("startTime={0}&endTime={1}&maxPageSize=31", this.userStartDate, this.userEndDate));
            }
        }

        // get hourly summary data
        private async void getHourlySummaryButton_Click(object sender, RoutedEventArgs e) {
            if (this.validateDates()) {
                this.secDelayRequest = 2;
                this.statusBar.Text = "Requesting data from MS Health Cloud...";
                await this.PerformRequest("Summaries/Hourly", string.Format("startTime={0}&endTime={1}&maxPageSize=48", this.userStartDate, this.userEndDate));
            }
        }

        // enable/disable individual activity checkboxes when "all" is selected
        private void optionActivitiesAll(object sender, RoutedEventArgs e) {
            if (this.checkActAll.IsChecked == true) {
                this.checkActRunning.IsEnabled = false;
                this.checkActRunning.IsChecked = false;
                this.checkActCycling.IsEnabled = false;
                this.checkActCycling.IsChecked = false;
                this.checkActWFree.IsEnabled = false;
                this.checkActWFree.IsChecked = false;
                this.checkActWGuide.IsEnabled = false;
                this.checkActWGuide.IsChecked = false;
                this.checkActGolf.IsEnabled = false;
                this.checkActGolf.IsChecked = false;
                this.checkActSleep.IsEnabled = false;
                this.checkActSleep.IsChecked = false;
            } else {
                this.checkActRunning.IsEnabled = true;
                this.checkActCycling.IsEnabled = true;
                this.checkActWFree.IsEnabled = true;
                this.checkActWGuide.IsEnabled = true;
                this.checkActGolf.IsEnabled = true;
                this.checkActSleep.IsEnabled = true;
            }
        }

        // download activities & parse options for that
        private async void getAcitvitiesButton_Click(object sender, RoutedEventArgs e) {
            bool activityEmpty = false;
            int pageSizeMod = 100;
            if (this.validateDates()) {
                string activityTypes = "&activityTypes=";
                string additionalOptions = "&activityIncludes=";
                if (this.checkActRunning.IsChecked == true) {
                    activityTypes = activityTypes + "Run,";
                }
                if (this.checkActCycling.IsChecked == true) {
                    activityTypes = activityTypes + "Bike,";
                }
                if (this.checkActWFree.IsChecked == true) {
                    activityTypes = activityTypes + "FreePlay,";
                }
                if (this.checkActWGuide.IsChecked == true) {
                    activityTypes = activityTypes + "GuidedWorkout,";
                }
                if (this.checkActGolf.IsChecked == true) {
                    activityTypes = activityTypes + "Golf,";
                }
                if (this.checkActSleep.IsChecked == true) {
                    activityTypes = activityTypes + "Sleep,";
                }
                if (activityTypes == "&activityTypes=" && this.checkActAll.IsChecked == false) {
                    this.statusBar.Text = "Please select an activity.";
                    activityEmpty = true;
                } else if (this.checkActAll.IsChecked == true) {
                    activityTypes = string.Empty;
                }
                activityTypes = activityTypes.TrimEnd((','));
                if (this.selOptionalData.SelectedIndex <= 0) {
                    this.secDelayRequest = 3;
                    additionalOptions = string.Empty;
                } else if (this.selOptionalData.SelectedIndex == 1) {
                    additionalOptions = additionalOptions + "Details,MapPoints";
                    this.secDelayRequest = 10;
                    pageSizeMod = 15;
                } else if (this.selOptionalData.SelectedIndex == 2) {
                    additionalOptions = additionalOptions + "MinuteSummaries";
                    this.secDelayRequest = 10;
                    pageSizeMod = 10;
                } 

                if (activityEmpty == false) {
                    this.statusBar.Text = "Requesting data from MS Health Cloud...";
                    await this.PerformRequest("Activities", string.Format("startTime={0}&endTime={1}{2}{3}&maxPageSize={4}", this.userStartDate, this.userEndDate, additionalOptions, activityTypes, pageSizeMod));
                }

            }
        }

        // save the data that was acquired to a text file
        private void saveAcquiredData(string fullTextReply, int newFileFlag) {
            if (newFileFlag == 1) {
                SaveFileDialog saveFileDialog1 = new SaveFileDialog();

                saveFileDialog1.Filter = "txt files (*.txt)|*.txt";
                saveFileDialog1.FilterIndex = 2;
                saveFileDialog1.Title = "Save BandSandbox Data";
                saveFileDialog1.ShowDialog();

                // If the file name is not an empty string open it for saving.
                if (saveFileDialog1.FileName != "") {
                    this.saveFilePath = saveFileDialog1.FileName;
                    StreamWriter file = new StreamWriter(saveFileDialog1.FileName);
                    file.WriteLine(fullTextReply);
                    file.Close();
                    this.statusBar.Text = "Data will be saved in: " + saveFileDialog1.FileName;
                } else {
                    this.saveFilePath = @".\ms_band_data.txt";
                    this.statusBar.Text = "No filename entered, defaulting to: ms_band_data.txt";
                    StreamWriter file = new StreamWriter(this.saveFilePath);
                    file.WriteLine(fullTextReply);
                    file.Close();
                }
            } else if (newFileFlag == 2) {
                using (StreamWriter file = File.AppendText(this.saveFilePath)) {
                    file.WriteLine(fullTextReply);
                }
            }
        }

        public static async Task pauseActionEvery(Action action, TimeSpan interval, int secDelay) {
            CancellationTokenSource cancellation = new CancellationTokenSource(TimeSpan.FromSeconds(secDelay));
            CancellationToken cancellationToken = cancellation.Token;
            while (true) {
                action();
                Task task = Task.Delay(interval, cancellationToken);

                try {
                    await task;
                }
                catch (TaskCanceledException) {
                    return;
                }
            }
        }

        // when requests have multiple pages of data, run through the pages
        //private async Task PaginatedRequest(string nextPageURL, string bandDataAcquired, bool morePages) {
        private async Task PaginatedRequest(string nextPageURL, string bandDataAcquired, bool morePages) {
            string respText = string.Empty;
            while (morePages == true) {
                try {
                    this.statusBar.Text = "Requesting data from MS Health Cloud...";
                    var uriBuilderNext = new UriBuilder(nextPageURL);
                    var request = HttpWebRequest.Create(uriBuilderNext.Uri);
                    this.statusURL.Text = uriBuilderNext.Uri.ToString();
                    request.Headers[HttpRequestHeader.Authorization] = string.Format("bearer {0}", this.creds.AccessToken);
                    try {
                        using (var response = await request.GetResponseAsync()) {
                            using (var stream = response.GetResponseStream()) {
                                using (var reader = new StreamReader(stream)) {
                                    respText = reader.ReadToEnd();
                                    this.responseText.Text = respText;
                                    this.saveAcquiredData(respText, 2);
                                    await pauseActionEvery(() => this.statusBar.Text = "Pausing between pages...", TimeSpan.FromSeconds(1), this.secDelayRequest);
                                }
                            }
                        }
                    } catch (WebException exception) {
                        if (exception.Status == WebExceptionStatus.ProtocolError) {
                            //Console.WriteLine(exception.Message);
                            await pauseActionEvery(() => this.statusBar.Text = "Pausing for 120s to overcome rate limit...", TimeSpan.FromSeconds(1), 120);
                            request.Abort();
                        } else {
                            throw;
                        }
                    }


                // "nextPage":"https://api.microsofthealth.net:443/v1/me/Summaries/Daily?ct=#################"
                string nextPageCheck = "\"nextPage\":\"https:.+?(?=\")";

                Match newData = System.Text.RegularExpressions.Regex.Match(respText, nextPageCheck, System.Text.RegularExpressions.RegexOptions.IgnoreCase);
                if (newData.Success) {
                    morePages = true;
                    nextPageURL = newData.Value.Remove(0, 12); // remove "nextPage":"
                } else {
                    morePages = false;
                        this.statusBar.Text = "Multi-page download complete.";
                }

                } catch (Exception ex) { 
                    this.statusBar.Text = string.Format("There was an error with your request. {0}", ex.Message);
                }
            }
        }

        // initial request -- hops to PaginatedRequest if there are multiple pages
        private async Task PerformRequest(string relativePath, string queryParams = null) {
            try {
                var uriBuilder = new UriBuilder(BaseHealthUri);
                uriBuilder.Path += relativePath;
                uriBuilder.Query = queryParams;
                var request = WebRequest.Create(uriBuilder.Uri);
                this.statusURL.Text = uriBuilder.Uri.ToString();
                request.Headers[HttpRequestHeader.Authorization] = string.Format("bearer {0}", this.creds.AccessToken);

                using (var response = await request.GetResponseAsync()) {
                    using (var stream = response.GetResponseStream()) {
                        using (var reader = new StreamReader(stream)) {
                            string bandDataAcquired = reader.ReadToEnd();
                            this.responseText.Text = bandDataAcquired;
                            this.saveAcquiredData(bandDataAcquired, 1);
                            // "nextPage":"https://api.microsofthealth.net:443/v1/me/Summaries/Daily?ct=#################"
                            string nextPageCheck = "\"nextPage\":\"https:.+?(?=\")";
                            Match newData = System.Text.RegularExpressions.Regex.Match(bandDataAcquired, nextPageCheck, System.Text.RegularExpressions.RegexOptions.IgnoreCase);
                            if (newData.Success) {
                                bool morePages = true;
                                string nextPageURL = newData.Value.Remove(0, 12); // remove "nextPage":"
                                //this.responseText.Text = nextPageURL;
                                await this.PaginatedRequest(nextPageURL, bandDataAcquired, morePages);
                            } else {
                                this.statusBar.Text = "Download complete.";
                            }
                        }
                    }
                }
            } catch (Exception ex) {
                this.statusBar.Text = string.Format("There was an error requesting the request. {0}", ex.Message);
            }
        }

        #endregion
        #region Sign-in and sign-out

        // authenticate w/ms health cloud
        private void authButton_Click(object sender, RoutedEventArgs e) {
            if (this.userAuthenticated == false) {
                UriBuilder uri = new UriBuilder("https://login.live.com/oauth20_authorize.srf");
                var query = new StringBuilder();
                query.AppendFormat("redirect_uri={0}", Uri.EscapeUriString(RedirectUri));
                query.AppendFormat("&client_id={0}", Uri.EscapeUriString(ClientId));
                query.AppendFormat("&scope={0}", Uri.EscapeUriString(Scopes));
                query.Append("&response_type=code");
                uri.Query = query.ToString();
                this.authButton.IsEnabled = false;
                this.authButton.Content = "Authenticating..";
                this.webView.Visibility = Visibility.Visible;
                this.webView.Navigate(uri.Uri);
            } else {
                UriBuilder uri = new UriBuilder("https://login.live.com/oauth20_logout.srf");
                var query = new StringBuilder();
                query.AppendFormat("redirect_uri={0}", Uri.EscapeUriString(RedirectUri));
                query.AppendFormat("&client_id={0}", Uri.EscapeUriString(ClientId));
                uri.Query = query.ToString();
                this.webView.Navigate(uri.Uri);
            }
        }

        private async void Browser_NavigationCompleted(object sender, NavigationEventArgs e) {
            // when browser navigates to redirect URI, extract auth code from URL & use it to fetch
            // access token -- if no authorization code is present, it's a sign-out flow.
            if (e.Uri.LocalPath.StartsWith("/oauth20_desktop.srf", StringComparison.OrdinalIgnoreCase)) {
                var decoder = System.Web.HttpUtility.ParseQueryString(e.Uri.Query);

                var code = decoder["code"];
                var error = decoder["error"];
                var errorDesc = decoder["error_description"];

                // is this sign-in or sign-out
                if (code != null) {
                    // hide the browser again
                    this.webView.Visibility = Visibility.Collapsed;

                    if (error != null) {
                        this.statusBar.Text = string.Format("{0}\r\n{1}", error, errorDesc);
                        return;
                    }

                    var tokenError = await this.GetToken(code, false);
                    if (string.IsNullOrEmpty(tokenError)) {
                        this.statusBar.Text = "Successful sign-in.";
                        this.selStartMonth.IsEnabled = true;
                        this.selStartDay.IsEnabled = true;
                        this.selStartYear.IsEnabled = true;
                        this.selEndYear.IsEnabled = true;
                        this.selEndMonth.IsEnabled = true;
                        this.selEndDay.IsEnabled = true;
                        this.startDateDT = DateTime.Now.AddMonths(-1);
                        this.endDateDT = DateTime.Now;
                        int yearIndex = this.startDateDT.Year;
                        this.selStartMonth.SelectedIndex = this.startDateDT.Month - 1;
                        this.selStartDay.SelectedIndex = this.todayDay - 1;
                        this.selStartYear.SelectedIndex = yearIndex - 2014;
                        this.selEndMonth.SelectedIndex = this.todayMonth - 1;
                        this.selEndDay.SelectedIndex = this.todayDay - 1;
                        this.selEndYear.SelectedIndex = this.todayYear - 2014;
                
                        this.userStartDate = startDateDT.ToString("O");
                        this.userEndDate = endDateDT.ToString("O");
                        this.getProfileButton.IsEnabled = true;
                        this.getDevicesButton.IsEnabled = true;
                        this.getActivitiesButton.IsEnabled = true;
                        this.getDailySummaryButton.IsEnabled = true;
                        this.getHourlySummaryButton.IsEnabled = true;
                        this.completeHistoryOpt.IsEnabled = true;
                        this.checkActRunning.IsEnabled = true;
                        this.checkActCycling.IsEnabled = true;
                        this.checkActWFree.IsEnabled = true;
                        this.checkActAll.IsEnabled = true;
                        this.checkActWGuide.IsEnabled = true;
                        this.checkActGolf.IsEnabled = true;
                        this.checkActSleep.IsEnabled = true;
                        this.selOptionalData.IsEnabled = true;
                        this.selOptionalData.SelectedIndex = 0;
                        this.authButton.IsEnabled = true;
                        this.authButton.Content = "Sign Out";
                        this.userAuthenticated = true;
                    } else {
                        this.statusBar.Text = tokenError;
                    }
                } else {
                    this.statusBar.Text = "Successful sign-out.";
                    this.selStartMonth.IsEnabled = false;
                    this.selStartDay.IsEnabled = false;
                    this.selStartYear.IsEnabled = false;
                    this.selEndYear.IsEnabled = false;
                    this.selEndMonth.IsEnabled = false;
                    this.selEndDay.IsEnabled = false;
                    this.authButton.IsEnabled = true;
                    this.getProfileButton.IsEnabled = false;
                    this.getDevicesButton.IsEnabled = false;
                    this.getActivitiesButton.IsEnabled = false;
                    this.getDailySummaryButton.IsEnabled = false;
                    this.getHourlySummaryButton.IsEnabled = false;
                    this.completeHistoryOpt.IsEnabled = false;
                    this.checkActRunning.IsEnabled = false;
                    this.checkActCycling.IsEnabled = false;
                    this.checkActWFree.IsEnabled = false;
                    this.checkActAll.IsEnabled = false;
                    this.checkActWGuide.IsEnabled = false;
                    this.checkActGolf.IsEnabled = false;
                    this.checkActSleep.IsEnabled = false;
                    this.selOptionalData.IsEnabled = false;
                    this.authButton.Content = "Sign In";
                    this.userAuthenticated = false;
                }
            }
        }

        private async Task<string> GetToken(string code, bool isRefresh) {
            UriBuilder uri = new UriBuilder("https://login.live.com/oauth20_token.srf");
            var query = new StringBuilder();
            query.AppendFormat("redirect_uri={0}", Uri.EscapeUriString(RedirectUri));
            query.AppendFormat("&client_id={0}", Uri.EscapeUriString(ClientId));
            query.AppendFormat("&client_secret={0}", Uri.EscapeUriString(ClientSecret));

            if (isRefresh) {
                query.AppendFormat("&refresh_token={0}", Uri.EscapeUriString(code));
                query.Append("&grant_type=refresh_token");
            } else {
                query.AppendFormat("&code={0}", Uri.EscapeUriString(code));
                query.Append("&grant_type=authorization_code");
            }

            uri.Query = query.ToString();
            var request = WebRequest.Create(uri.Uri);

            try {
                using (var response = await request.GetResponseAsync()) {
                    using (var stream = response.GetResponseStream()) {
                        using (var streamReader = new StreamReader(stream)) {
                            var responseString = streamReader.ReadToEnd();
                            var jsonResponse = JObject.Parse(responseString);
                            this.creds.AccessToken = (string)jsonResponse["access_token"];
                            this.creds.ExpiresIn = (long)jsonResponse["expires_in"];
                            this.creds.RefreshToken = (string)jsonResponse["refresh_token"];
                            string error = (string)jsonResponse["error"];

                            return error;
                        }
                    }
                }
            } catch (Exception ex) {
                return ex.Message;
            }
        }
        #endregion

        private void exitAppButton_Click(object sender, RoutedEventArgs e) {
            Application.Current.Shutdown();
        }
    }
}
