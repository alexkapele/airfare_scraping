def get_google_flights_data(origin,dest,date,currency,non_stop=True,save_csv=True):

    import os
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.chrome.options import Options
    from bs4 import BeautifulSoup
    import time
    
    import pandas as pd
    import re
    from datetime import datetime
        
    #Set up driver
    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    
    chrome_options = Options()
    chrome_options.add_experimental_option("prefs", {
            "download.default_directory": os.getcwd()+"\\Downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing_for_trusted_sources_enabled": False,
            "safebrowsing.enabled": False})
    
    headless = True
    
    if headless == True:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(executable_path=os.getcwd()+"/chromedriver.exe",desired_capabilities=caps,chrome_options=chrome_options)
    
    #Search parameters
    #origin = 'ATH'
    #dest = 'SKG'
    #date = '2020-06-15'
    #currency = 'GBP'
    #non_stop = True
    
    if non_stop:
        params = 'e:1;s:0;sd:1;t:f;tt:o' #url end if non-stop is selected
    else:
        params = ';e:1;sd:1;t:f;tt:o' #url end if non-stop isn't selected
    
    #Load website
    url = 'https://www.google.com/flights?hl=en' + '#flt=' + origin + '.' + dest + '.' + date + ';c:' + currency + params
    driver.get(url)
    time.sleep(5)
    
    soup=BeautifulSoup(driver.page_source, 'lxml')
    
    #Extract airline names
    airlines = []
    for airline in soup.find_all('span', attrs={'class': 'gws-flights__ellipsize'}):
        airlines.append(airline.getText())
    airlines = airlines[::2]
    airlines
    
    #Extract times
    times = []
    for time_ in soup.find_all('div', attrs={'class': 'gws-flights-results__times flt-subhead1'}):
        times.append(time_.getText()[2:-3])
    times
    
    #Extract prices (cheapest and other)
    prices = []
    for price in soup.find_all('div', attrs={'class': 'flt-subhead1 gws-flights-results__price gws-flights-results__cheapest-price'}) :
        prices.append(price.getText()[6:-3])
    
    for price in soup.find_all('div', attrs={'class': 'flt-subhead1 gws-flights-results__price'}) :
        prices.append(price.getText()[6:-3])
    prices = prices[::2]
    prices
    
    #Create dataframe to store data
    data = pd.DataFrame()
    
    #Store extracted values
    data['Airline'] = airlines
    data['Time'] = times
    data['Price'] = prices
    
    #Separate dep and arr times
    data['Dep Time (local)'] = data['Time'].str.split('–').str[0]
    data['Arr Time (local)'] = data['Time'].str.split('–').str[1]
    data['Arr Time (local)'] = data['Arr Time (local)'].str.strip()
    data = data.drop(['Time'], axis=1)
    
    #Seperate price and currency
    #data['Currency'] = data['Price'].apply(lambda x: x[:re.search(r"\d", x).start()])
    data['Currency'] = currency
    data['Price'] = data['Price'].apply(lambda x: x[re.search(r"\d", x).start():])
    
    #Add Other info
    data['Origin'] = origin
    data['Destination'] = dest
    data['Flight Date'] = date
    data['Flight Date'] = pd.to_datetime(data['Flight Date'])
    data['Weekday'] = data['Flight Date'].dt.weekday_name
    data['Fare Extraction Date'] = datetime.today().strftime('%Y-%m-%d')
    data['Fare Extraction Date'] = pd.to_datetime(data['Fare Extraction Date'])
    
    #Reorder columns
    data = data[['Origin','Destination','Airline','Flight Date','Weekday','Dep Time (local)', 'Arr Time (local)', 'Price', 'Currency', 'Fare Extraction Date']]
    
    #Save data
    if save_csv:
        filename = origin + '-' + dest + '_' + 'fares.csv'
        if os.path.exists(os.getcwd()+'/Downloads/' + filename):
            data_full = pd.read_csv(os.getcwd()+'/Downloads/' + filename)
            data_full['Flight Date'] = pd.to_datetime(data_full['Flight Date'])
            data_full['Fare Extraction Date'] = pd.to_datetime(data_full['Fare Extraction Date'])
            data_full = data_full.append(data, ignore_index=True)
            data_full.to_csv(os.getcwd() + '/Downloads/' + filename, index=False)
        else:
            data.to_csv(os.getcwd() + '/Downloads/' + filename, index=False)


    return data