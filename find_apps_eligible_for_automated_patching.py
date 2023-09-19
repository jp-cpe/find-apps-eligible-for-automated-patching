#!/usr/bin/env python3

import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URLs of the webpages to scrape
url1 = "https://learn.jamf.com/bundle/jamf-app-catalog/page/App_Installers_Software_Titles.html"
url2 = "https://github.com/Installomator/Installomator/blob/main/Installomator.sh"

# Set to store software titles with responses from the API
titles_with_responses_url1 = set()
titles_with_responses_url2 = set()

# Replace with your Jamf instance URL and API token
JAMF_URL = "your_jamf_url_goes_here"
API_TOKEN = "your_jamf_api_bearer_token_goes_here"

# Function to call the Jamf API and check if a software title exists
def check_jamf_api(software_title):
    encoded_title = urllib.parse.quote(software_title)
    api_url = f"{JAMF_URL}/JSSResource/computerapplications/application/{encoded_title}.app"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        # Parse the XML response
        xml_response = ET.fromstring(response.text)
        
        # Find <version> elements
        version_elements = xml_response.findall(".//version")
        
        # Check if any <version> element has a <serial_number>
        for version_element in version_elements:
            computers_element = version_element.find("computers")
            if computers_element is not None:
                computer_element = computers_element.find("computer")
                if computer_element is not None:
                    serial_number_element = computer_element.find(".//serial_number")
                    if serial_number_element is not None:
                        return True
        
        return False
    else:
        # Handle specific HTTP status codes with error messages
        if response.status_code == 400:
            print("Error 400: Bad request. Verify the syntax of the request, specifically the request body.")
        elif response.status_code == 401:
            print("Error 401: Authentication failed. Verify the credentials being used for the request.")
        elif response.status_code == 403:
            print("Error 403: Invalid permissions. Verify the account being used has the proper permissions for the resource you are trying to access.")
        elif response.status_code == 404:
            print("Error 404: Resource not found. Verify the URL path is correct.")
        elif response.status_code == 409:
            print("Error 409: The request could not be completed due to a conflict with the current state of the resource.")
        elif response.status_code == 414:
            print("Error 414: Request-URI too long.")
        elif response.status_code == 500:
            print("Error 500: Internal server error. Retry the request or contact support if the error persists.")
        elif response.status_code == 503:
            print("Error 503: Service unavailable.")
        else:
            print(f"Unexpected error with status code {response.status_code}")
        
        return False

# Separate scrape_and_check function for url1
def scrape_and_check_url1(url, titles_with_responses):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)
    time.sleep(5)  # Wait for page to load dynamically
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Locate the correct div element for "Software Titles" using the specific ID
    software_titles_div = soup.find("div", id="reference-7022__d3e80")
    
    if software_titles_div:
        list_items = software_titles_div.find_all("li")  # Find all <li> elements within the div
        for item in list_items:
            software_title = item.get_text().strip()
            print(f"Checking {software_title}...")
            if check_jamf_api(software_title):
                titles_with_responses.add(software_title)
                print(f"Found in Jamf API: {software_title}")
            else:
                print(f"Not found in Jamf API: {software_title}")
    else:
        print("Software Titles section not found.")
    
    driver.quit()

# Separate scrape_and_check function for url2
def scrape_and_check_url2(url, titles_with_responses):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(url)
    
    try:
        # Wait for the <textarea> element to be present
        textarea_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "read-only-cursor-text-area"))
        )
        
        # Extract the text content from the <textarea> element
        software_titles_text = textarea_element.text
        
        # Split the text content by newline to get individual titles
        app_names = software_titles_text.split('\n')
        elements_with_name = [software_title.split('name="')[1].split('"')[0] for software_title in app_names if 'name="' in software_title]

        # Remove duplicates by converting to a set and back to a list
        unique_elements = list(set(elements_with_name))

        for software_title in unique_elements:
            software_title = software_title.strip().title()
            print(f"Checking {software_title}...")
            if check_jamf_api(software_title):
                titles_with_responses.add(software_title)
                print(f"Found in Jamf API: {software_title}")
            else:
                print(f"Not found in Jamf API: {software_title}")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Scrape and check titles from the first URL
    scrape_and_check_url1(url1, titles_with_responses_url1)

    # Scrape and check titles from the second URL
    scrape_and_check_url2(url2, titles_with_responses_url2)

    # Print the titles that received responses from both URLs
    common_titles = titles_with_responses_url1.intersection(titles_with_responses_url2)
    
    print("\nApplications in your mac environment that can have patching automated by Jamf App Installers:")
    for title in sorted(titles_with_responses_url1):
        print(title)
    
    print("\nApplications in your mac environment that can have patching automated by the Installomator script:")
    for title in sorted(titles_with_responses_url2):
        print(title)
    
    if common_titles:
        print("\nApplications in your mac environment that can have patching automated by either Jamf App Installers or the Installomator script:")
        for title in sorted(common_titles):
            print(title)
    else:
        print("\nNo titles appeared in both lists.")
