from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time as t
import pandas as pd
import tqdm

driver = webdriver.Safari()

#Setup the Crawler
def crawler_setup():
    driver.get('https://www.glassdoor.com/profile/login_input.htm')
    return

def find_id(id=None):
    '''This method simplifies the Selenium method that searchs the HTML by an ID.'''
    return driver.find_element(By.ID, id)

def find_xpath(xpath=None):
    '''This method simplifies the Selenium method that searchs the HTML by an XPATH.'''
    return driver.find_element(By.XPATH, xpath)

def find_css(css=None):
    '''This method simplifies the Selenium method that searchs the HTML by an CSS Selectors.'''
    return driver.find_element(By.CSS_SELECTOR, css)

def button_click(xpath=None):
    '''This method simplifies the process of clicking a button defined by an XPATH in the HTML.'''
    button_click = find_xpath(xpath).click()
    return

def get_content(xpath=True, element=None):
    '''This method simplifies the process of getting content (<p>, <h1>, etc.) out of a Selenium Web Object found
    by an XPATH or CSS Selector.'''
    content = find_xpath(element).text if xpath == True else find_css(element).text
    return content

def signin_protocol(username=None, password=None):
    '''This method populates the signin form and clicks signin to the main webpage.'''
    #Locate the Sign-In Elements
    email_field_element = find_id('userEmail').send_keys(username)
    password_field_element = find_id('userPassword').send_keys(password)
    button_click(xpath='//*[@id="InlineLoginModule"]/div/div/div[1]/div[4]/form/div[3]/div[1]/button')
    return

def location_(city=None, state=None):
    '''This method populates the location field within the page header. '''
    job_location = driver.find_element_by_id('sc.location')
    location = job_location.send_keys(f'{city}, {state}')
    return

def job_title(job_title=None):
    '''This method populates the job title field within the page header.'''
    job_element = driver.find_element_by_id('sc.keyword')
    job = job_element.send_keys(job_title)
    return

def get_job_information():
    '''This method collects the job information for a single job list item in the MainCol Section of the search page. '''
    job_title = get_content(element='//*[@id="HeroHeaderModule"]/div[3]/div[1]/h1')
    company_name = get_content(element='//*[@id="HeroHeaderModule"]/div[3]/div[1]/p')
    company_rank = get_content(element='//*[@id="HeroHeaderModule"]/div[3]/div[3]/span[1]/text()[1]')
    job_desc = get_content(xpath=False,element='div.jobDescriptionContent.desc')
    try:
        salary_estimate = get_content('//*[@id="HeroHeaderModule"]/div[3]/div[4]/div/span/text()')
    except:
        salary_estimate = None
    return [job_title, company_name, company_rank, salary_estimate, job_desc]

def get_all_jobs_on_page():
    ''''''
    page_listings = []
    job_info = get_job_information()
    page_listings.append(job_info)
    for i in tqdm(range(1,30)):
        button_click(xpath=f"//li[@class='jl'][{i}]")
        t.sleep(5)
        if i == 1:
            button_click(xpath='//*[@id="JAModal"]/div/div[2]/div/div[1]')
            job_info = get_job_information()
            page_listings.append(job_info)
            t.sleep(5)
        else:
            job_info = get_job_information()
            page_listings.append(job_info)
            t.sleep(5)
    df = pd.DataFrame(page_listings, columns=['job_title', 'company_name', 'company_rank', 'salary_estimate', 'job_desc'])
    return df

def get_next_page():
    ''''''
    return

def job_search(username=None, password=None, title=None, city=None, state=None):
    ''''''
    crawler_setup()
    signin_protocol(username=username, password=password)
    t.sleep(3)
    job_title(job_title=title)
    t.sleep(3)
    location_(city=city, state=state)
    t.sleep(2)
    button_click(xpath='//*[@id="HeroSearchButton"]')
    return

if __name__ == "__main__":
    job_search(username='', password='', title='Data Scientist', city='Indianapolis', state='IN')
    t.sleep(6)
    df = get_all_jobs_on_page()
    df.head()
    #get_job_information()
