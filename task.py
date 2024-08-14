import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to your WebDriver executable
webdriver_path = r'C:\Users\nithin\OneDrive\Desktop\pyhton-task\chromedriver-win64\chromedriver.exe'

service = Service(webdriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# List of job search URLs
job_search_urls = [
    "https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_TPR=r86400&f_C=1586&position=1&pageNum=0"
]



def get_job_details(job_element):
    """Extracts job details from the job element."""
    job_info = {}

    # Extract company name
    try:
        company = job_element.find("h4", class_="base-search-card__subtitle").find("a").get_text(strip=True)
    except AttributeError:
        company = None
    job_info["company"] = company

    # Extract job title
    try:
        title = job_element.find("h3", class_="base-search-card__title").get_text(strip=True)
    except AttributeError:
        title = None
    job_info["title"] = title

    # Extract LinkedIn job ID
    try:
        job_id = job_element.find("a", {"data-tracking-control-name": "public_jobs_jserp-result_search-card"})["href"].split("?")[0].split("-")[-1]
    except (AttributeError, IndexError):
        job_id = None
    job_info["job_id"] = job_id

    # Extract location
    try:
        job_location = job_element.find("span", class_="job-search-card__location").get_text(strip=True)
    except AttributeError:
        job_location = None
    job_info["location"] = job_location

    # Extract posted date
    try:
        posted_info = job_element.find("time", class_="job-search-card__listdate--new").get_text(strip=True)
        posted_date = convert_posted_date(posted_info)
    except AttributeError:
        posted_info = None
        posted_date = None
    job_info["posted_info"] = posted_info
    job_info["posted_date"] = posted_date

    # Extract employment type (if available elsewhere)
    try:
        employment = job_element.find(By.XPATH,"/html/body/div[5]/div[3]/div[4]/div/comment()[2]").get_text(strip=True)
    except AttributeError:
        employment = None
    job_info["employment_type"] = employment

    # Extract seniority level (if available elsewhere)
    try:
        seniority = job_element.find("span", class_="job-details-jobs-unified-top-card__job-insight-view-model-secondary").get_text(strip=True)
    except AttributeError:
        seniority = None
    job_info["seniority_level"] = seniority
        
    return job_info

# Helper functions
def convert_posted_date(posted_info):
    """Converts the posted date text into a formatted date string."""
    today = datetime.now()
    posted_info = posted_info.lower()
    if 'hour' in posted_info:
        return today.strftime("%d-%m-%Y")
    if 'today' in posted_info:
        return today.strftime("%d-%m-%Y")
    elif 'week' in posted_info:
        try:
            days_ago = int(posted_info.split(' ')[0])
            return (today - timedelta(days=days_ago)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    elif 'month' in posted_info:
        try:
            months_ago = int(posted_info.split(' ')[0])
            return (today - timedelta(days=months_ago * 30)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    elif 'day' in posted_info:
        try:
            days_ago = int(posted_info.split(' ')[0])
            return (today - timedelta(days=days_ago)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    return None

def fetch_job_data(url):
    """Fetches job data from the given LinkedIn URL."""
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_elements = soup.find_all("div", {"class": "job-search-card"})

    job_list = []
    for job_element in job_elements:
        job_details = get_job_details(job_element)
        if job_details:
            job_list.append(job_details)

    return job_list

# Main script
all_job_data = []
for url in job_search_urls:
    job_data = fetch_job_data(url)
    all_job_data.extend(job_data)

# Save data to JSON
with open('job_data.json', 'w') as json_file:
    json.dump(all_job_data, json_file, indent=4)

# Save data to CSV
data_frame = pd.DataFrame(all_job_data)
data_frame.to_csv('job_data.csv', index=False)

# Clean up
driver.quit()

print("Scraping completed. Data saved to job_data.json and job_data.csv.")


