def get_google_flights_data(origin,dest,dates,currency,non_stop=True,save_csv=True,headless=True):

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
    
    
    if headless == True:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(executable_path=os.getcwd()+"/chromedriver.exe",desired_capabilities=caps,chrome_options=chrome_options)
    
   
    if non_stop:
        params = 'e:1;s:0;sd:1;t:f;tt:o' #url end if non-stop is selected
    else:
        params = ';e:1;sd:1;t:f;tt:o' #url end if non-stop isn't selected
    
    #Create dataframes to store data for the date and all dates combined
    data = pd.DataFrame()
    
    
    for i, date in enumerate(dates):
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
        
        
        data_date = pd.DataFrame()
        
        if airlines: #check if there are any flights on the selected date
            
            #Store extracted values
            data_date['Airline'] = airlines
            data_date['Time'] = times
            data_date['Price'] = prices
            
            #Separate dep and arr times
            data_date['Dep Time (local)'] = data_date['Time'].str.split('–').str[0]
            data_date['Arr Time (local)'] = data_date['Time'].str.split('–').str[1]
            data_date['Arr Time (local)'] = data_date['Arr Time (local)'].str.strip()
            data_date = data_date.drop(['Time'], axis=1)
            
            #Seperate price and currency
            data_date['Currency'] = currency
            data_date['Price'] = data_date['Price'].apply(lambda x: x[re.search(r"\d", x).start():])
            
            #Add Other info
            data_date['Origin'] = origin
            data_date['Destination'] = dest
            data_date['Flight Date'] = date
            data_date['Flight Date'] = pd.to_datetime(data_date['Flight Date'])
            data_date['Weekday'] = data_date['Flight Date'].dt.weekday_name
            data_date['Fare Extraction Date'] = datetime.today().strftime('%Y-%m-%d')
            data_date['Fare Extraction Date'] = pd.to_datetime(data_date['Fare Extraction Date'])
            
            #Reorder columns
            data_date = data_date[['Origin','Destination','Airline','Flight Date','Weekday','Dep Time (local)', 'Arr Time (local)', 'Price', 'Currency', 'Fare Extraction Date']]
            
            #Append date's results to data
            data = data.append(data_date, ignore_index=True)
            
            #Print progress indicator 
            print(str(i+1) + '/' + str(len(dates)) + ' days scraped')
            
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