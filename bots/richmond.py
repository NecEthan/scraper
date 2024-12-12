import json
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
import re
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup  
import requests
import datetime
import json


def richmond_bot(startdate, enddate, wordlist):

    def format_address(addresss):
        formatted_address = addresss.replace('\n', ' ')
        address_list.append(formatted_address)

    def convert(s):
        # initialization of string to ""
        new = ""

        # traverse in the string
        for x in s:
            new = new + x + '|'

        # return string
        return new

    row_list = []
    address_list = []
    name_list = []
    data = []
    print(wordlist)
    words = convert(wordlist)
    print(words)
    words_search_for = words.rstrip(words[-1])
    parsed_startdate = pd.to_datetime(startdate, format="%Y-%m-%d")
    parsed_enddate = pd.to_datetime(enddate, format="%Y-%m-%d")
    reversed_startdate = parsed_startdate.strftime('%d/%m/%Y')
    reversed_enddate = parsed_enddate.strftime('%d/%m/%Y')

    formatted_start_date = parsed_startdate.strftime('%m/%d/%y')
    formatted_end_date = parsed_enddate.strftime('%m/%d/%y')


    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    url = 'https://www2.richmond.gov.uk/lbrplanning/Planning_Report.aspx'
    driver.get(url)

    # Input start and end dates
    input_element1 = driver.find_element(By.ID, 'ctl00_PageContent_dpValFrom')
    input_element2 = driver.find_element(By.ID, 'ctl00_PageContent_dpValTo')
    input_element1.send_keys(reversed_startdate)
    input_element2.send_keys(reversed_enddate)

    search_element = driver.find_element(By.CLASS_NAME, 'btn-primary')
    time.sleep(3)
    close = driver.find_element(By.ID, 'ccc-close')
    close.click()

    num_results_element = Select(driver.find_element(By.ID, 'ctl00_PageContent_ddLimit'))
    num_results_element.select_by_visible_text('500')
    search_element.click()

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'infocontent')))

    # Get the page source after the search
    page_source = driver.page_source

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    span_div = driver.find_element(By.ID, 'ctl00_PageContent_lbl_APPS')
    num_results = span_div.find_element(By.TAG_NAME, 'strong')

    if (int(num_results.text) == 500):
        driver.quit()
    else:
        searchResultsPage = soup.find('ul', class_='planning-apps')
        searchResults = searchResultsPage.find_all('li')

        row_list = []

        for row in searchResults:
            address_divs = row.find_all('p')
            address_desc = address_divs[1].text

            if (re.search(words_search_for, words, flags=re.I)):
                row_list.append(row)

        for row in row_list:
            address_div = row.find('h3')
            address = address_div.text.strip()
            format_address(address)

            a_tag = row.find('a')
            href_value = a_tag.get('href')
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@href='{href_value}']"))
            )
            element.click()

            try:
                subtab = driver.find_element(By.ID, 'ctl00_PageContent_btnShowApplicantDetails')
            except:
                driver.back()
                name_list.append('n/a')
                continue

            subtab.click()
            wait.until(EC.presence_of_element_located((By.ID, 'ctl00_PageContent_lbl_Applic_Name')))
            name_page_source = driver.page_source
            name_soup = BeautifulSoup(name_page_source, 'html.parser')
            name = name_soup.find('span', id='ctl00_PageContent_lbl_Applic_Name')
            name_list.append(name.text.strip())

            driver.back()
            driver.back()

        merge_data = zip(name_list, address_list)
        for item in merge_data:
            data.append(item)

    driver.quit()
    print(len(data))
    website_name = "richmond"
    now = datetime.datetime.now()
    scraped_at = now.strftime("%m/%d/%y")

    data_to_send = [
        {
            "websiteName": website_name,
            "name": name,
            "address": address,
            "startDate": formatted_start_date, 
            "endDate": formatted_end_date,  
            "scrapedAt": scraped_at
        }
        for name, address in data
    ]
    print(data_to_send)

    # API endpoint
    # api_url = "http://localhost:8080/scrape/save"
    api_url = "https://council-data-hub-backend-production.up.railway.app/scrape/save"

    # Send the POST request
    response = requests.post(api_url, json=data_to_send)

    # Check response
    if response.status_code == 200:
        print("Data saved successfully!")
    else:
        print(f"Failed to save data: {response.status_code}")
        print(response.text)



richmond_bot('2023-09-05', '2023-09-05', ['tree', 'rear'])


