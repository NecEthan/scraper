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
from bs4 import BeautifulSoup  # Added import for BeautifulSoup


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

    words = convert(wordlist)
    words_search_for = words.rstrip(words[-1])
    parsed_startdate = pd.to_datetime(startdate, format="%Y-%m-%d")
    parsed_enddate = pd.to_datetime(enddate, format="%Y-%m-%d")
    reversed_startdate = parsed_startdate.strftime('%d/%m/%Y')
    reversed_enddate = parsed_enddate.strftime('%d/%m/%Y')

    chrome_options = Options()
    chrome_options.add_argument('--headless')
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

            if (re.search(words_search_for, address_desc, flags=re.I)):
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

    # Return the result as a JSON string
    print(data)
    print(json.dumps(data))  # Print JSON to stdout
    return data


richmond_bot('2020-02-02', '2020-02-05', 'tree')
