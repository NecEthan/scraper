from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from datetime import datetime, timedelta
import re
import time
import requests
import urllib3
import random

def southwark_bot(wordlist, current_date):

    # start_date = datetime.now() - timedelta(days=2)

    # for i in range(2):
        # current_date = start_date + timedelta(days=i)
        formatted_date = current_date.strftime('%Y-%m-%d')  
        reversed_date = current_date.strftime('%d/%m/%Y')  
        print(reversed_date)

        time.sleep(random.uniform(5, 15)) 

        
        print(f"Scraping for date: {reversed_date}")

        def convert(s):
            new = ""
            for x in s:
                new = new + x + '|'
            return new

        # Suppress only the InsecureRequestWarning from urllib3 needed for your request
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        words = convert(wordlist)
        words_search_for = words.rstrip(words[-1])

        # Lists to store data
        row_list = []
        address_list = []
        name_list = []
        data = []

        # Set up the WebDriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('headless') 
        driver = webdriver.Chrome(options=chrome_options)

        base_url = 'https://planning.lambeth.gov.uk'
        url = 'https://planning.lambeth.gov.uk/online-applications/search.do?action=advanced'

        try:
            driver.get(url)
            time.sleep(random.uniform(1, 3))  
        except Exception as e:
            print(f"An error occurred while loading the page: {e}")
            driver.quit()
            raise

        # Input start and end dates
        try:
            time.sleep(random.uniform(3, 8))  
            wait = WebDriverWait(driver, 40)
            input_element1 = wait.until(EC.presence_of_element_located((By.ID, 'applicationReceivedStart')))
            input_element2 = wait.until(EC.presence_of_element_located((By.ID, 'applicationReceivedEnd')))
            input_element1.send_keys(reversed_date)
            input_element2.send_keys(reversed_date)
            time.sleep(random.uniform(2, 5))  
        except NoSuchElementException:
            print("Date input elements not found. Skipping this step or retrying...")
        except TimeoutException:
            print("Date input elements did not appear within the timeout period.")
        
        time.sleep(random.uniform(1, 3))  


        # Click the search button
        try:
            search_element = driver.find_element(By.CLASS_NAME, 'recaptcha-submit')
            search_element.click()
            time.sleep(random.uniform(1, 3)) 
        except NoSuchElementException:
            print("Search button not found. Skipping this step or retrying...")
            driver.refresh()
            try:
                search_element = driver.find_element(By.CLASS_NAME, 'recaptcha-submit')
                search_element.click()
                time.sleep(random.uniform(1, 3)) 
            except TimeoutException:
                print("Element not found after second attempt. Exiting.")


        try: 
            message_box = driver.find_element(By.CLASS_NAME, 'messagebox')
            if message_box:
                print('successfully found no data')
                driver.quit()
                return
                # continue
        except Exception:
            print('data found')

        # Wait for the page to load
        try:
            wait = WebDriverWait(driver, 40)
            wait.until(EC.presence_of_element_located((By.ID, 'resultsPerPage')))
            time.sleep(random.uniform(2, 4)) 
        except TimeoutException:
            print("Timed out waiting for page to load. Retrying...")
            driver.refresh()
            try:
                wait.until(EC.presence_of_element_located((By.ID, 'resultsPerPage')))
                time.sleep(random.uniform(2, 4)) 
            except TimeoutException:
                print("Element not found after second attempt. Exiting.")

        # Select 100 and submit to show max results
        try:
            num_results_element = Select(driver.find_element(By.ID, 'resultsPerPage'))
            num_results_element.select_by_visible_text('100')
            num_results_go = driver.find_element(By.CLASS_NAME, 'primary')
            num_results_go.click()
            time.sleep(random.uniform(1, 2)) 
        except NoSuchElementException:
            print("Results per page dropdown not found. Skipping this step or retrying...")

        next_a_tag = None
        multiple_pages = True
        num_results = 0

        while multiple_pages:
            try:
                wait = WebDriverWait(driver, 40)
                wait.until(EC.presence_of_element_located((By.ID, 'resultsPerPage')))
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                time.sleep(random.uniform(1, 3)) 

                searchResultsPage = soup.find('div', class_='col-a')
                searchResults = searchResultsPage.find_all('li', class_='searchresult')

                row_list = []

                for row in searchResults:
                    address_div = row.find('a')
                    address_desc = address_div.text
                    time.sleep(random.uniform(1, 3)) 


                    if re.search(words_search_for, address_desc, flags=re.I):
                        row_list.append(row)

                print(len(row_list))
                num_results += len(row_list)

                for row in row_list:
                    address_div = row.find('p', class_='address')
                    address = address_div.text.strip()
                    address_list.append(address)
                    print(address)

                    a_tag = row.find('a')
                    href_value = a_tag.get('href')
                    time.sleep(random.uniform(1, 3)) 

                    test_url = f'{base_url}{href_value}'
                    time.sleep(random.uniform(1, 3)) 
                    try:
                        summary_page = requests.get(test_url, verify=False)
                        summary_page.raise_for_status()
                        time.sleep(random.uniform(3, 6)) 
                        summary_soup = BeautifulSoup(summary_page.content, "html.parser")
                        time.sleep(random.uniform(3, 6)) 

                        info_tab = summary_soup.find(id='subtab_details')
                        info_href = info_tab.get('href')
                        info_atag = f'{base_url}{info_href}'

                        further_info = requests.get(info_atag, verify=False)
                        time.sleep(random.uniform(1, 3)) 

                        further_info_soup = BeautifulSoup(further_info.content, "html.parser")
                        time.sleep(random.uniform(3, 6))  

                        applicant_row = further_info_soup.find('th', string='Applicant Name').find_next('td')
                        applicant_name = applicant_row.get_text(strip=True)

                        print(applicant_name)
                        name_list.append(applicant_name)
                    except requests.exceptions.RequestException as e:
                        print(f"Request failed: {e}. Retrying...")
                        time.sleep(5)
                        continue

                try:
                    next_a_tag = driver.find_element(By.CLASS_NAME, 'next')
                    action = ActionChains(driver)
                    action.move_to_element(next_a_tag).click().perform()
                    time.sleep(random.uniform(2, 4)) 
                except NoSuchElementException:
                    multiple_pages = False
                    print("No more pages found")
                except StaleElementReferenceException:
                    print("Stale element")
                    next_a_tag = driver.find_element(By.CLASS_NAME, 'next')
                    next_a_tag.click()
                    time.sleep(random.uniform(2, 4)) 

            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

        # Merge and format data
        merge_data = zip(name_list, address_list)
        for item in merge_data:
            data.append(item)

        date = pd.to_datetime(reversed_date, format='%d/%m/%Y', errors='coerce')
        formatted_date = date.strftime('%d/%m/%y')  
        print(formatted_date)

        website_name = "lambeth"

        data_to_send = [
            {
                "websiteName": website_name,
                "name": name,
                "address": address,
                "date": formatted_date
            }
            for name, address in data
        ]
        print(data_to_send)

        api_url = "https://council-data-hub-backend-production.up.railway.app/scrape/save"
        response = requests.post(api_url, json=data_to_send)
        if response.status_code == 200:
            print("Data saved successfully!")
            driver.quit()
        else:
            print(f"Failed to save data: {response.status_code}")
            print(response.text)
            return


start_date = datetime(2025, 2, 1) 
end_date = datetime(2025, 2, 13)  
current_date = start_date  

while current_date <= end_date:
    print(f"Scraping for date: {current_date.strftime('%d/%m/%Y')}")

    southwark_bot(['extension', 'loft'], current_date)  

    time.sleep(100) 

    current_date += timedelta(days=1)

print("Scraping completed. Exiting.")