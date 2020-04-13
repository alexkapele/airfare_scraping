import os
import pandas as pd
from google_flights_scraper import get_google_flights_data
from datetime import timedelta, date


def daterange(date1, date2):
    date1 = date(int(date1[:4]),int(date1[5:7]),int(date1[8:10]))
    date2 = date(int(date2[:4]),int(date2[5:7]),int(date2[8:10]))
    dates = []
    for n in range(int ((date2 - date1).days)+1):
        date_ = date1 + timedelta(n)
        dates.append(date_.strftime("%Y-%m-%d"))
    return dates

#Scraping parameters
origin = 'ATH'
dest = 'SKG'
currency = 'GBP'
non_stop = True

#Scraping dates
start_date = '2020-06-20'
end_date = '2020-06-22'
dates = daterange(start_date, end_date)


data = pd.DataFrame()
for date_ in dates:
    data = data.append(get_google_flights_data(origin,dest,date_,currency,non_stop=True,save_csv=False),ignore_index=True)


filename = origin + '-' + dest + '_' + 'fares.csv'
if os.path.exists(os.getcwd()+'/Downloads/' + filename):
    data_full = pd.read_csv(os.getcwd()+'/Downloads/' + filename)
    data_full['Flight Date'] = pd.to_datetime(data_full['Flight Date'])
    data_full['Fare Extraction Date'] = pd.to_datetime(data_full['Fare Extraction Date'])
    #Need to add check to ensure that existing dates are overwritten
    data_full = data_full.append(data, ignore_index=True)
    data_full.to_csv(os.getcwd() + '/Downloads/' + filename, index=False)
else:
    data.to_csv(os.getcwd() + '/Downloads/' + filename, index=False)

