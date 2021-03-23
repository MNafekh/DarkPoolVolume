import urllib
import statistics
import holidays
import numpy as np
from datetime import date, datetime, timedelta
from prettytable import PrettyTable

dts = datetime.today().strftime('%Y%m%d')
weekago = (datetime.today() - timedelta(days=7)).strftime('%Y%m%d')
hdays = []
dayrange = 28

# consolidated file: http://regsho.finra.org/CNMSshvol20201013.txt
url = "http://regsho.finra.org/CNMSshvol" + dts + ".txt"
pasturl = "http://regsho.finra.org/CNMSshvol" + weekago + ".txt"

# returns dates for the last two weeks of weekdays
def daterange():
    start_date = datetime.today() - timedelta(days=dayrange)
    end_date = datetime.today()
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

# searches file for given ticker and stores data in array
def findTicker(ticker, file):
    tkrdata = []
    for line in file: 
        tkrdata = line.decode("utf-8").split("|")
        if len(tkrdata) > 2: # look for complete line
            if tkrdata[1] == ticker: # found ticker in data
                return tkrdata
    return []

def getHolidays(year):
    for d in holidays.UnitedStates(years=year).items():
        hdays.append(d[0].strftime('%Y%m%d'))
    return hdays

def getVolume(ticker: str, t):
    ticker = ticker.upper()
    float_pcts = []
    for d in daterange(): # populate list of short float values for date range in chronological order
        if d.isoweekday() in range(1, 6) and d.strftime('%Y%m%d') not in getHolidays(d.year): # skip weekends and holidays
            url = "http://regsho.finra.org/CNMSshvol" + d.strftime("%Y%m%d") + ".txt"
            file = urllib.request.urlopen(url)
            dp = findTicker(ticker, file)
            if len(dp) > 1:
                float_pcts.append(int(dp[2]) / int(dp[4])) # store an array of the float values
            else:
                pass

    if len(float_pcts) > 1:
        latest = round(100 * float_pcts.pop(), 2)
        avg = round(100 * statistics.mean(float_pcts[-5:]), 2)
        n = np.array(float_pcts)
        ten_pct = round(100 * np.percentile(n, 10), 2)
        nty_pct = round(100 * np.percentile(n, 90), 2)
        if latest > nty_pct or latest < ten_pct or avg > nty_pct or avg < ten_pct:
            t.add_row([ticker, latest, avg, ten_pct, nty_pct])
    return t
            
