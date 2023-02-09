""" File that contains all pure data scraping functionality, to scrape general lists of content from websites """

from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

from src.util.config import config


def open_link_with_cookies(driver, link):
    """ Open website link and load cookies from /res/cookies for that website. After, reload to apply the cookies """

    cookie_path = f"res/cookies/{link.split('.')[1]}.txt"
    driver.get(link)
    with open(cookie_path, 'r') as f:
        cookies = {}
        for line in f:
            parts = line.split('\t')
            cookies[parts[0]] = parts[1]
    for cookie in cookies:
        driver.add_cookie({"name": cookie, "value": cookies[cookie]})
    driver.get(link)


def get_elements_count(driver, scraper_config):
    """ Scrape the total number of content elements on the website. Used to iterate over all pages """

    # get element counter info
    if 'id' in scraper_config['number_elements']:
        num_results = driver.find_element(by=By.ID, value="pagination").text
    if 'selector' in scraper_config['number_elements']:
        num_results = driver.find_element(by=By.CSS_SELECTOR, value=scraper_config['number_elements']['selector']).text
    # extract number of results
    if 'text_split' in scraper_config['number_elements']:
        split_text, split_index = scraper_config['number_elements']['text_split']
        num_results = num_results.split(split_text)[split_index]
    # convert element counter to int
    num_results = num_results.replace('.', '').replace(',', '')
    num_results = int(num_results)
    print(f"RESULTS: {num_results} - Dauer: {round(num_results * scraper_config['time_estimation'])} Min.")

    return num_results


def open_next_page(driver, scraper_config):
    """ Configurable way to open the next page of the website, according to the scraper config

    Currently supported:
    - link_offset: add an offset to a variable of the link
        - e.g. ...&page=1 -> ..&page=2 for variable 'page' and offset 1
    - selector: click on an element with a specific selector
    """

    if 'link_offset' in scraper_config['next_page']:
        # get current link from driver
        current_link = driver.current_url
        page_variable = scraper_config['next_page']['link_offset']['variable_name']
        # extract offset from current link
        current_offset = int(current_link.split(f'{page_variable}=')[1].split('&')[0])
        new_offset = current_offset + scraper_config['next_page']['link_offset']['offset']
        new_link = current_link.replace(f"{page_variable}={current_offset}", f"{page_variable}={new_offset}")
        driver.get(new_link)
    elif 'selector' in scraper_config['next_page']:
        next_page_button = driver.find_element(by=By.CSS_SELECTOR, value=scraper_config['next_page']['selector'])
        next_page_button.click()


def get_element_values(content_element, scraper_config):
    """
    Configurable way to extract the values from a content holder element, according to the scraper config

    Currently supported element specifiers:
    - class: choose the element with a specific css class

    Currently supported 'output' specifiers:
    - text: get the text of the element
    - href: get the href attribute of the element
    - img_base64: get the base64 encoded image of the element (significantly slower)
    """
    result_values = {}
    for value_name in scraper_config['values']:
        value = scraper_config['values'][value_name]
        try:
            if 'class' in value:
                value_containing_element = content_element.find_element(by=By.CLASS_NAME, value=value['class'])

            # get value from element
            if 'output' in value and value['output'] == 'text':
                result_values[value_name] = value_containing_element.text
            elif 'output' in value and value['output'] == 'href':
                result_values[value_name] = value_containing_element.get_attribute('href')
            elif 'output' in value and value['output'] == 'img_base64':
                result_values[value_name] = value_containing_element.screenshot_as_base64
        except:
            result_values[value_name] = None
            print(f"ERROR: {value_name} not found")

    return result_values


def scrape_all_elements_one_page(driver, scraper_config):
    """ Scrapes all elements on one page of the website, using 'element_class' to find the content elements """

    # print all elements with class list-item-content using find_elements
    if 'page_sleep' in scraper_config:
        sleep(scraper_config['page_sleep'])
    content_elements = driver.find_elements(by=By.CLASS_NAME, value=scraper_config['element_class'])
    results = []
    for content_element in content_elements:
        result_values = get_element_values(content_element=content_element, scraper_config=scraper_config)
        results.append(result_values)

    # get df from results
    df = pd.DataFrame(results)

    return df


def scrape_all_pages(driver, scraper_config):
    """ Scrapes all pages of the website and returns & saves the results as a dataframe to output/websites """

    link = scraper_config['link']
    open_link_with_cookies(driver=driver, link=link)
    sleep(1)  # extra sleep to avoid 'too many forwardings' error
    if 'number_elements' in scraper_config:
        num_results = get_elements_count(driver=driver, scraper_config=scraper_config)
    else:
        num_results = 1000
    df = scrape_all_elements_one_page(driver=driver, scraper_config=scraper_config)

    # get all elements
    while len(df) < num_results:
        open_next_page(driver=driver, scraper_config=scraper_config)
        df = pd.concat([df, scrape_all_elements_one_page(driver, scraper_config=scraper_config)])
    driver.quit()

    df.drop_duplicates(inplace=True)
    df['website'] = scraper_config['link'].split('.')[1]
    df.to_csv(f'output/websites/{scraper_config["link"].split(".")[1]}.csv', index=False)

    return df


if __name__ == "__main__":

    scrape_all_pages(scraper_config=config['SCRAPER']['FREELANCE'])
    scrape_all_pages(scraper_config=config['SCRAPER']['UPWORK'])
    scrape_all_pages(scraper_config=config['SCRAPER']['FREELANCERMAP'])
